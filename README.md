# arewefluentyet.com

The code to generate the data is in `src/arewefluentyet`.

The data is in `data/revs.txt` and `data/progress.json`.

To update the data, you need to have a check-out of `master` for the code,
and of `gh-pages` for the data.

This requires the [`version-control-tools/hgext/mozext`](https://hg.mozilla.org/hgcustom/version-control-tools/)
mercurial extension to be enabled in your `mozilla-central` clone, for
`pushhead` and `pushdate` to work. At the time of this writing, `mozext`
is compatible with [mercurial versions 4.3 - 4.6](https://bugzilla.mozilla.org/show_bug.cgi?id=1482325).

Update your `mozilla-central` clone to the corresponding revision.

The actual data bit is in `arewefluentyet.data.Aggregator`. Use that class like so

```python
# adjust this path to your local check-out of the gh-pages branch
REPO = "gh-pages/arewefluentyet.com"
from datetime import date, datetime, timedelta
import json
import subprocess
from arewefluentyet import data

revs = open(REPO + "/data/revs.txt").read()
global_json = json.load(open(REPO + "/data/progress.json"))
last_date = date(*(int(s) for s in revs.split()[-2].split("-")))
today = datetime.utcnow().date()
week = timedelta(days=7)

aggregator = data.Aggregator(
    ["browser/locales/l10n.toml"]
)
aggregator.load()

this_date = last_date + week
while this_date < today:
  date_stamp = this_date.isoformat()
  rev = subprocess.check_output([
    'hg', 'log',
    '-l', '1',
    '-T{node|short}',
    '-r',
    'reverse(pushhead("central") and pushdate("<{} 00:00"))'.format(
      date_stamp
    )
  ]).decode('utf-8')
  subprocess.check_call([
    "hg", "update", "-r", rev
  ])
  revs += "{} {}\n".format(date_stamp, rev)
  global_json.append({
      "date": date_stamp,
      "revision": rev,
      "data": aggregator.gather()
  })
  open(REPO + "/data/revs.txt", "w").write(revs)
  json.dump(
      global_json, open(REPO + "/data/progress.json", "w"),
      indent=0,
      separators=(",", ": "),
      sort_keys=True,
  )
  this_date += week
```
