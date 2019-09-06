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


def run_app(params, args, get_data, main):
    parser = argparse.ArgumentParser(
        description='Aggregate M1 data for arewefluentyet.com')
    if "mc" in args:
        parser.add_argument('--mc',
                            required=True,
                            metavar='../mozilla-unified',
                            help='Path to mozilla-central clone')
    if "dump-log" in args:
        parser.add_argument('--dump-log',
                            required=True,
                            metavar='../mozilla-unified/data-20190819.txt',
                            help='Path to the dump file')
    parser.add_argument('--gh-pages-data',
                        required=True,
                        metavar='../awfy/gh-pages/data',
                        help='Path to a data directory of a arewefluentyet.com/gh-pages clone')

    result = parser.parse_args()

    data_path = os.path.join(result.gh_pages_data, params["milestone"])

    if not is_file_writable(data_path, "progress.json"):
        parser.error("{} path is not writable!".format(
            os.path.join(data_path, "progress.json")))
    if not is_file_writable(data_path, "snapshot.json"):
        parser.error("{} path is not writable!".format(
            os.path.join(data_path, "snapshot.json")))

    if "mc" in args:
        if not is_dir_readable(result.mc):
            parser.error("{} path is not readable!".format(result.mc))
    if "dump-log" in args:
        if not is_dir_readable(result.dump_log):
            parser.error("{} path is not readable!".format(result.dump_log))

    main(result, data_path, get_data, params)
