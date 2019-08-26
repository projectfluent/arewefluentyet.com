import os
import subprocess
import json
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