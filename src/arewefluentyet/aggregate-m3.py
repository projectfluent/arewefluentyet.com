from data import Aggregator
import os
from collections import defaultdict
from datetime import date, timedelta

from helper_mc import main
from helper import run_app

PARAMS = {
    "start_date": date(2017, 11, 1),
    "milestone": "M3",
    "frequency": timedelta(days=7),
}


def extract_progress(dataset):
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


def get_data(mc_path, next_date, next_revision):
    aggregator = Aggregator(
        [os.path.join(mc_path, "browser/locales/l10n.toml")])
    aggregator.load()

    result = aggregator.gather()

    (entries, progress) = extract_progress(result)
    return (entries, progress)


if __name__ == "__main__":
    run_app(PARAMS, ["mc"], get_data, main)
