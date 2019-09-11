import re
import os
import sys
import argparse
import subprocess
from datetime import date, timedelta

from helper import switch_to_revision, run_app

PARAMS = {
    "start_date": date(2019, 8, 25),
    "milestone": "M2",
    "frequency": timedelta(days=7),
    "log_dir": "startup_log",
    "bookmark": "collect-startup-entries",
}


def parse_stack(stack):
    result = []

    for line in stack.split("\n"):
        if len(line.strip()) == 0:
            continue
        match = re.match("([0-9]+) (.*?) \[\"([^\"]+)\"\:([0-9]+)\:([0-9]+)\]", line)
        if match is None:
            print(line)
            continue
        result.append({
            "index": match.group(1),
            "call": match.group(2),
            "path": match.group(3),
            "line": match.group(4),
            "col": match.group(5),
        })
    return result


def find_context(contexts, pos):
    for context in contexts:
        if context["from"] <= pos and (context["to"] >= pos or context["to"] is None):
            return context
    return None


def extract_progress(raw_data):
    contexts = []
    entries = []

    matches = re.finditer("DTD base/url: ([^,]+), (.*)", raw_data)
    for match in matches:
        if len(contexts) == 0 or contexts[-1]["origin"] != match.group(1):
            if len(contexts) > 0:
                contexts[-1]["to"] = match.start()

            new_context = {
                "from": match.start(),
                "to": match.end(),
                "origin": match.group(1),
                "files": [match.group(2)]
            }
            contexts.append(new_context)
        else:
            contexts[-1]["files"].append(match.group(2))
            contexts[-1]["to"] = match.end()

    matches = re.finditer("== Entry ==(.*?)== Entry End ==", raw_data, re.DOTALL | re.MULTILINE)
    for match in matches:
        entry = {
            "type": None,
            "id": None,
            "stack": None,
            "file": None,
            "stack": None,
        }
        stack = False
        for line in match.group(1).replace("\\n", "\n").split("\n"):
            if line.startswith("type: "):
                entry["type"] = line[6:]
            elif line.startswith("id: "):
                entry["id"] = line[4:]
            elif line.startswith("origin: "):
                entry["stack"] = line[9:]
            elif line.startswith("stack:"):
                stack = True
                entry["stack"] = ""
            elif stack and len(line) > 0:
                entry["stack"] += line + "\n"
        if entry["stack"] is not None:
            entry["stack"] = parse_stack(entry["stack"])

        if entry["type"] == "dtd":
            context = find_context(contexts, match.start())
            if context:
                entry["stack"] = context["origin"]
                entry["file"] = context["files"][0]

        entries.append(entry)

    progress = {
        "ftl": 0,
        "dtd": 0,
        "properties": 0
    }
    for entry in entries:
        progress[entry["type"]] += 1

    return (entries, progress)


def get_bookmark_parent(mc_path, bookmark):
    rev = subprocess.check_output([
        "hg", "log",
        "--cwd", mc_path,
        "-r", bookmark,
        "-T", "{p1.node}",
    ]).decode('utf-8')

    return rev


def rebase_bookmark(mc_path, next_revision, bookmark):
    parent = get_bookmark_parent(mc_path, bookmark)
    if parent != next_revision:
        subprocess.run([
            "hg", "rebase", "--cwd", mc_path, "-s", bookmark, "-d", next_revision
        ], check=True, stdout=subprocess.DEVNULL)


def build_firefox(mc_path):
    cmd = os.path.join(mc_path, "mach")
    with open("firefox-build-log.txt", "w") as fp:
        subprocess.run([cmd, "build"], stdout=fp, check=True)


def collect_log(mc_path, log_name, next_date, next_revision):
    data_dir = os.path.join(mc_path, "startup_log")
    data_file = os.path.join(data_dir, log_name)
    cmd = os.path.join(mc_path, "mach")
    with open(data_file, "w") as fp:
        fp.write("revision: {}\n".format(next_revision))
        fp.write("date: {}\n".format(next_date))
        subprocess.run([cmd, "run", "--temp-profile"], stdout=fp, check=True)


def get_data(mc_path, next_date, next_revision):
    log_name = "data-{}.txt".format(next_date.strftime("%Y%m%d"))
    log_path = os.path.join(mc_path, PARAMS["log_dir"], log_name)

    if os.path.exists(log_path):
        print("Using log for {} ({}).".format(next_revision, log_name))
        raw_data = open(log_path).read()
        (entries, progress) = extract_progress(raw_data)
        return (entries, progress)

    response = input("About to attempt to apply the `collect-startup-entries` onto {} (Y/N): ".format(next_revision))
    if response.lower() != "y":
        exit()
    rebase_bookmark(mc_path, next_revision, PARAMS["bookmark"])
    switch_to_revision(PARAMS["bookmark"], mc_path)

    response = input("About to build Firefox with the `collect-startup-entries` (Y/N): ")
    if response.lower() != "y":
        exit()

    build_firefox(mc_path)

    response = input("About to launch Firefox with `collect-startup-entries` (Y/N): ")
    if response.lower() != "y":
        exit()

    collect_log(mc_path, log_name, next_date, next_revision)

    raw_data = open(log_path).read()
    (entries, progress) = extract_progress(raw_data)
    return (entries, progress)


if __name__ == "__main__":
    run_app(PARAMS, get_data)
