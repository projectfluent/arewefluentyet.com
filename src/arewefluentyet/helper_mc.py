import subprocess

from helper import read_progress_data, parse_date, write_data


def get_current_revision(mc_path):
    rev = subprocess.check_output([
        "hg", "id", "--cwd", mc_path, "-T{id}"
    ]).decode("utf-8")
    return rev


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
        "hg", "id", "--cwd", mc_path, "-r", rev, "-T", "{pushdate|shortdate}"
    ]).decode("utf-8")
    return parse_date(rev)


def switch_to_revision(rev, mc_path):
    subprocess.check_call([
        "hg", "update", "--cwd", mc_path, "-c", "-r", rev
    ], stdout=subprocess.PIPE)


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


def main(arg_result, gh_pages_data_path, get_data, params):
    mc_path = arg_result.mc
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
            response = input("Do you want to collect date for it (Y/N): ")
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
