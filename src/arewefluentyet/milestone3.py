from data import Aggregator
import os
from collections import defaultdict
from datetime import date
from milestone import Milestone


class Milestone3(Milestone):
    name = "M3"
    start_date = date(2017, 11, 1)

    def get_data(self, source, date, revision):
        aggregator = Aggregator(
            [os.path.join(source.path, "browser/locales/l10n.toml")])
        aggregator.load()

        result = aggregator.gather()

        (entries, progress) = self.extract_progress(result)
        return (entries, progress)

    def extract_progress(self, dataset):
        entries = []
        progress = defaultdict(int)

        for subset in dataset:
            for path, count in subset.items():
                ext = os.path.splitext(path)[1]
                if not ext:
                    continue
                if ext.startswith("."):
                    ext = ext[1:]
                if ext:
                    progress[ext] += count
                entries.append({"file": path, "count": count})

        return (entries, progress)
