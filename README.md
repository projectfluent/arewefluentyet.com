# arewefluentyet.com

The code to generate the data is in `src/arewefluentyet`.

The data is in `data/M[1-3]/snapshot.json` and `data/[M[1-3]/progress.json`.

To update the data, you need to have a check-out of `master` for the code,
and of `gh-pages` for the data.

This requires the [`version-control-tools/hgext/pushlog`](https://hg.mozilla.org/hgcustom/version-control-tools/)
mercurial extension to be enabled in your `mozilla-central` clone, for
`pushhead` and `pushdate` to work.

The aggregator for M1 and M3 can be called like this:

```bash
python ./src/arewefluentyet/aggregate.py -m M1 -m M3 --mc ~/projects/mozilla-unified --gh-pages-data ~/projects/awfy/gh-pages/data
```

Alternatively, `-m all` will enable all three milestones.

If you want to just collect data from the current revision, `--use-current-revision` will do just that.

A `--dry-run` is also available for testing purposes.

