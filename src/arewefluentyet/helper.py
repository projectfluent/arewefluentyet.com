import os
import subprocess
import json
import argparse
from datetime import date, datetime, timedelta


def read_progress_data(data_path):
    path = os.path.join(data_path, "progress.json")

    if os.path.exists(path):
        return json.load(open(path))

    print("Warning: \"{}\" doesn't exist. Creating a new one.".format(path))

    return []


def parse_date(input):
    return date(*(int(s) for s in input.split("-")))


def pick_next_revision(next_date, mc_path):
    rev = subprocess.check_output([
        "hg", "log",
        "--cwd", mc_path,
        "-l", "1",
        "-T", "{node}",
        "-r",
        "reverse(pushhead() and pushdate('< {}') and ::central)".format(next_date)
    ]).decode('utf-8')

    return rev


def get_current_revision(mc_path):
    rev = subprocess.check_output([
        "hg", "id", "--cwd", mc_path, "-T{id}"
    ]).decode("utf-8")
    return rev


def get_revision_date(rev, mc_path):
    rev = subprocess.check_output([
        "hg", "id", "--cwd", mc_path, "-r", rev, "-T", "{date|shortdate}"
    ]).decode("utf-8")
    return parse_date(rev)


def switch_to_revision(rev, mc_path):
    subprocess.check_call([
        "hg", "update", "--cwd", mc_path, "-c", "-r", rev
    ], stdout=subprocess.PIPE)


def write_data(progress_data, snapshot_data, data_path):
    json.dump(
        progress_data,
        open(os.path.join(data_path, "progress.json"), "w"),
        indent=0,
        separators=(",", ": "),
        sort_keys=True,
    )

    json.dump(
        snapshot_data,
        open(os.path.join(data_path, "snapshot.json"), "w"),
        indent=0,
    )


def is_file_writable(path, f):
    if os.path.exists(os.path.join(path, f)):
        return os.access(os.path.join(path, f), os.W_OK)
    return os.access(path, os.W_OK)


def is_dir_readable(path):
    return os.access(path, os.R_OK)


def main(mc_path, gh_pages_data_path, get_data, params):
    start_revision = get_current_revision(mc_path)
    print("Your current revision is: {}.".format(start_revision))

    progress_data = read_progress_data(gh_pages_data_path)

    any_update_happened = False

    last_date = params["start_date"]
    last_revision = None

    if progress_data:
        last_date = parse_date(progress_data[-1]["date"])
        last_revision = progress_data[-1]["revision"]

    while True:
        next_date = last_date + params["frequency"]
        next_revision = pick_next_revision(next_date, mc_path)
        if next_revision == last_revision:
            break

        next_rev_date = get_revision_date(next_revision, mc_path)
        if next_rev_date < next_date:
            print("The next scheduled date for data collection is {}".format(next_date))
            print("But the latest available revision is from {}".format(next_rev_date))
            response = input("Do you want to collect date for it (Y/N):")
            if response.lower() != "y":
                break

        snapshot_data = update_data(progress_data, next_revision, next_date, mc_path, get_data)
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


def run_app(params, get_data):
    parser = argparse.ArgumentParser(
        description='Aggregate M1 data for arewefluentyet.com')
    parser.add_argument('--mc',
                        required=True,
                        metavar='../mozilla-unified',
                        help='Path to mozilla-central clone')
    parser.add_argument('--gh-pages-data',
                        required=True,
                        metavar='../awfy/gh-pages/data',
                        help='Path to a data directory of a arewefluentyet.com/gh-pages clone')

    args = parser.parse_args()

    data_path = os.path.join(args.gh_pages_data, params["milestone"])

    if not is_file_writable(data_path, "progress.json"):
        parser.error("{} path is not writable!".format(
            os.path.join(data_path, "progress.json")))
    if not is_file_writable(data_path, "snapshot.json"):
        parser.error("{} path is not writable!".format(
            os.path.join(data_path, "snapshot.json")))
    if not is_dir_readable(args.mc):
        parser.error("{} path is not readable!".format(args.mc))

    main(args.mc, data_path, get_data, params)


def update_data(progress_data, next_revision, next_date, mc_path, get_data):
    current_revision = get_current_revision(mc_path)

    if current_revision != next_revision:
        print("Updating repository to revision: {} ({}).".format(
            next_revision, next_date))
        switch_to_revision(next_revision, mc_path)
    else:
        print("Collecting data for revision: {} ({}).".format(
            next_revision, next_date))

    (entries, progress) = get_data(mc_path, next_date, next_revision)

    snapshot = {"date": str(next_date), "revision": next_revision, "data": entries}

    progress_data.append({
        "data": progress,
        "date": snapshot["date"],
        "revision": snapshot["revision"],
    })

    return snapshot
