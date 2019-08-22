from data import Aggregator
import os
import json
import argparse
from collections import defaultdict
from datetime import date, timedelta

from helper import read_progress_data, parse_date, \
    pick_next_revision, get_current_revision, \
    switch_to_revision, write_data, is_file_writable, is_dir_readable

START_DATE = date(2017, 11, 1)
FREQUENCY = timedelta(days=7)


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


def update_data(progress_data, next_revision, next_date, mc_path):
    current_revision = get_current_revision(mc_path)

    if current_revision != next_revision:
        print("Updating repository to revision: {} ({}).".format(
            next_revision, next_date))
        switch_to_revision(next_revision, mc_path)
    else:
        print("Collecting data for revision: {} ({}).".format(
            next_revision, next_date))

    aggregator = Aggregator(
        [os.path.join(mc_path, "browser/locales/l10n.toml")])
    aggregator.load()

    result = aggregator.gather()

    (entries, progress) = extract_progress(result)

    progress_data.append({
        "data": progress,
        "date": str(next_date),
        "revision": next_revision,
    })

    snapshot = {"date": str(next_date), "revision": next_revision, "data": entries}
    return snapshot


def main(mc_path, gh_pages_data_path):
    start_revision = get_current_revision(mc_path)
    print("Your current revision is: {}.".format(start_revision))

    progress_data = read_progress_data(gh_pages_data_path)

    any_update_happened = False

    last_date = START_DATE
    last_revision = None

    if progress_data:
        last_date = parse_date(progress_data[-1]["date"])
        last_revision = progress_data[-1]["revision"]

    while True:
        next_date = last_date + FREQUENCY
        next_revision = pick_next_revision(next_date, mc_path)
        if next_revision == last_revision:
            break

        snapshot_data = update_data(progress_data, next_revision, next_date, mc_path)
        any_update_happened = True

        last_date = next_date
        last_revision = next_revision

    end_revision = get_current_revision(mc_path)
    if start_revision != end_revision:
        print("Switching back to start revision: {}.".format(start_revision))
        switch_to_revision(start_revision, mc_path)

    if not any_update_happened:
        print("Could not find a revision for the next data update!")
    else:
        print("DONE!")
        write_data(progress_data, snapshot_data, gh_pages_data_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Aggregate M3 data for arewefluentyet.com')
    parser.add_argument('--mc',
                        required=True,
                        metavar='../mozilla-unified',
                        help='Path to mozilla-central clone')
    parser.add_argument('--gh-pages-data',
                        required=True,
                        metavar='../awfy/gh-pages/data',
                        help='Path to a data directory of a arewefluentyet.com/gh-pages clone')

    args = parser.parse_args()

    data_path = args.gh_pages_data
    if not is_file_writable(data_path, "progress.json"):
        parser.error("{} path is not writable!".format(
            os.path.join(data_path, "progress.json")))
    if not is_file_writable(data_path, "snapshot.json"):
        parser.error("{} path is not writable!".format(
            os.path.join(data_path, "snapshot.json")))
    if not is_dir_readable(args.mc):
        parser.error("{} path is not readable!".format(args.mc))

    main(args.mc, args.gh_pages_data)
