# arewefluentyet.com

The code to generate the data is in `src/arewefluentyet`.

The interesting bit is in `arewefluentyet.data.Aggregator`. Use that class like so

```python
from arewefluentyet import data
aggregator = data.Aggregator(
    ["browser/locales/l10n.toml", "mobile/android/locales/l10n.toml"]
)
aggregator.load()
global_json.append({
    "date": "yyyy-mm-dd",
    "revision": "abcdef",
    "data": agg.gather()
})
```
