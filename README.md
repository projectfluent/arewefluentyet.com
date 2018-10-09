# arewefluentyet.com

The code to generate the data is in `src/arewefluentyet`.

The data is in `data/revs.txt` and `data/progress.json`.

To update the data, find the relevant push for Sunday by running

```bash
for d in 2018-10-14; do
  hg log -r "reverse(pushhead(\"central\") and pushdate(\"<$d 00:00\"))" -l 1 -T"$d {node|short}\n" >> data/revs.txt
done
```

Update your `mozilla-central` clone to the corresponding revision.

The actual data bit is in `arewefluentyet.data.Aggregator`. Use that class like so

```python
import json
from arewefluentyet import data
aggregator = data.Aggregator(
    ["browser/locales/l10n.toml", "mobile/android/locales/l10n.toml"]
)
aggregator.load()
global_json.append({
    "date": "yyyy-mm-dd",
    "revision": "abcdef",
    "data": aggregator.gather()
})
json.dump(
    global_json, open(".../progress.json", "w"),
    indent=0,
    separators=(",", ": "),
    sort_keys=True,
)
```
