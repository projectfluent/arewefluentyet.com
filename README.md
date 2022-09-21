# arewefluentyet.com

The following instructions are for unix-based systems.

## Code Organization

The code to generate the data is in the `main` branch, located in `src/arewefluentyet`.

The data is in the `gh-pages` branch, located in `data/M[1-3]/snapshot.json` and `data/M[1-3]/progress.json`.

## Directory Structure

To update the data, you need to have two separate checkouts: one of the `main` branch for the code, and one of the `gh-pages` branch for the data.

You will also need a mercurial (`hg`) checkout of the `mozilla-unified` repository. You can follow instructions to set up `mozilla-unified` with mercurial for your operating system [here](https://firefox-source-docs.mozilla.org/setup/).

Here is an example directory tree:

```
.
├── awfy-data        // a checkout of the gh-pages branch
├── awfy-gen         // a checkout of the main branch
└── mozilla-unified  // a mercurial checkout of mozilla-unified
```

Note: the names `awfy-data` and `awfy-gen` are arbitrary. These are just the names I chose for my two directories.

You can clone them via command line:

```
$ git clone -b main https://github.com/projectfluent/arewefluentyet.com awfy-gen
$ git clone -b gh-pages https://github.com/projectfluent/arewefluentyet.com awfy-data
```

## Mercurial Setup

Now that you have your directory structure set up, generating the data requires the [`version-control-tools/hgext/pushlog`](https://hg.mozilla.org/hgcustom/version-control-tools/) Mercurial extension to be enabled in your `mozilla-unified` clone, for `pushhead` and `pushdate` to work.

Open your `hgrc` (`$HOME/.hgrc`) file in your preferred text editor and add the following to your `[extensions]` section:

```
[extensions]
pushlog = $HOME/.mozbuild/version-control-tools/hgext/pushlog
```

Now you need to verify that everything is working. To do this, you'll need to find the date for which the `gh-pages` branch was last updated with data. Navigate to that directory, and run a `git log` to check the most recent commit message.

For example, if the most recent date is `2021-08-13`, you'll want to collect data for the date that is 7 days after this: `2021-08-20`.

Next, navigate to your `mozilla-unified` directory and run this command with your target date:

```
hg log -l 1 -T "{node}" -r "reverse(pushhead() and pushdate('< 2021-08-20') and ::central)"
```

If everything is working, you should see a commit hash, such as `7af78405aade4dbd64f4c713dc3feeed5d8ffa5b`.

If the command doesn't return any value, and you have just enabled the `pushlog` extension, make sure to pull content again with `hg pull -u` in the `mozilla-unified` clone. Note that this might take several minutes.

## Generating Data for M1 and M3

Aggregating data for `M1` and `M3` can be done by statically analyzing the repository.

Collecting data for `M2` is slightly more involved and requires building Firefox to log data at runtime. This will be covered in the next section.

The aggregator for `M1` and `M3` can be called like this:

```
python3 <path_to_master_branch_checkout>/src/arewefluentyet/aggregate.py -m M1 -m M3 --mc <path_to_mozilla_unified_checkout> --gh-pages-data <path_to_gh-pages_branch_checkout>/data
```

With the proposed structure, the command will look like this:

```
.
├── awfy-data
├── awfy-gen
└── mozilla-unified

$ python3 awfy-gen/src/arewefluentyet/aggregate.py -m M1 -m M3 --mc mozilla-unified --gh-pages-data awfy-data/data
```

* Similarly, passing `-m M2` will enable the `M2` milestone (covered in next section).
* Alternatively, `-m all` will enable all three milestones.
* If you want to just collect data from the current revision, `--use-current-revision` will do just that.
* A `--dry-run` is also available for testing purposes.

Go ahead and try updating `M1` and `M3` with the command above.

While the program is running, your terminal screen will occasionally go blank and display `(END)`. This is just output from various commands the script is running; exit out of the screen by pressing `q`, and the script will continue.

If you are running the script on a later date than your target date, the script may ask you:

```
But the latest available revision is 7857f4c37a928c219638460c7048940a78bbf1ba (2021-08-24)
Do you want to collect date for it (Y/N):
```

You can select `N` for this option.

If all is successful, you should see output like this:

```
Your current revision is: 7857f4c37a928c219638460c7048940a78bbf1ba
The first date we need to collect data for is: 2021-08-20

Selected revision: 7af78405aade4dbd64f4c713dc3feeed5d8ffa5b (2021-08-20)
 - Updating to revision
720 files updated, 0 files merged, 25 files removed, 0 files unresolved
 - Collecting data
   - M1: Writing
   - M3: Writing
```

And you can verify the changes by navigating to the `gh-pages` branch directory and running `git status`.

```
modified:   data/M1/progress.json
modified:   data/M1/snapshot.json
modified:   data/M3/progress.json
modified:   data/M3/snapshot.json
```

Congratulations! You just updated `M1` and `M3`.

## Generating Data for M2

As mentioned before, generating data for `M2` is more involved and requires building and launching Firefox to collect data at runtime.

In order to do this, you need to patch on some special logging that this tool expects to see while Firefox is running.

**IMPORTANT**: this requires a full build, an artifact build won't be sufficient. Check the `mozconfig` file in your `mozilla-unified` clone, and comment out or remove the line `ac_add_options --enable-artifact-builds` before proceding.

First, let's make sure you're up to date with the latest central by navigating to your `mozilla-unified` checkout and running

```
hg pull --rebase default
hg up default
```

Next, you need to grab the patch with the logging changes by pulling them from this revision: https://phabricator.services.mozilla.com/D40217

```
moz-phab patch D40217
```

This will check out a bookmark called `phab-D40217`, but the tool requires that the bookmark is called `collect-startup-entries`, so you need to rename it:

```
hg bookmark --rename phab-D40217 collect-startup-entries
```

You should now be ready to run the script for `M2`. With the proposed structure, the command will look like this:

```
.
├── awfy-data
├── awfy-gen
└── mozilla-unified

$ python3 awfy-gen/src/arewefluentyet/aggregate.py -m M2 --mc mozilla-unified --gh-pages-data awfy-data/data
```

Following the prompts will be similar to `M1` and `M3`, but this time it will ask you to apply the `collect-startup-entries` onto the target date's commit.

```
About to attempt to apply the `collect-startup-entries` onto 7af78405aade4dbd64f4c713dc3feeed5d8ffa5b (Y/N):
```

Say `Y` to this.

Next, it will ask you:

```
(activating bookmark collect-startup-entries)
About to build Firefox with the `collect-startup-entries` (Y/N):
```

Also say `Y` to this.

This will then begin building Firefox on the commit for the target date with the special logging enabled. **This may take a while**.

You can monitor the progress by opening a new terminal tab, navigating to the directory from which you invoked the Python command, and typing:

```
tail -f firefox-build-log.txt
```

Once your build is finished, in the terminal tab where the Python script is running, it will prompt you to open Firefox:

```
About to launch Firefox with `collect-startup-entries` (Y/N):
```

Say `Y` to this, then wait for the home page to load. Give it a slow three-second count before closing out of Firefox again.

The runtime logging should be complete, and you should be able to verify that it collected the data by navigating to your `gh-pages` checkout directory and running `git status`

```
modified:   data/M2/progress.json
modified:   data/M2/snapshot.json
```

If you are running the script on a later date than your target date, the script may then ask you:

```
But the latest available revision is 7857f4c37a928c219638460c7048940a78bbf1ba (2021-08-24)
Do you want to collect date for it (Y/N):
```

Say `N` to this.

Congratulations! You have now updated `M2`.

### Troubleshooting

The script to generate data for `M2` stores a TXT file in `mozilla-unified/startup_log`, e.g. `data-2021-08-20.txt`. If you need to repeat the data generation, you need to remove this file and reset the content of the `gh-pages` clone.

## Committing the Data

Once you've generated new data for `M1`, `M2`, and `M3`, you may want to serve the static site locally to view the update yourself. For example, you can run `python -m http.server 8000` from the folder with the `gh-pages` clone.

Ultimately, you will need to add the changes as a commit on the `gh-pages` branch and push them to the repository.

```
modified:   data/M1/progress.json
modified:   data/M1/snapshot.json
modified:   data/M2/progress.json
modified:   data/M2/snapshot.json
modified:   data/M3/progress.json
modified:   data/M3/snapshot.json
```
