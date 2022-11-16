import argparse
import os
from milestone1 import Milestone1
from milestone2 import Milestone2
from milestone3 import Milestone3
from source import Source
from datetime import timedelta

PARAMS = {
    "frequency": timedelta(days=7),
    "dry_run": False,
}

Milestones = list[Milestone1 | Milestone2 | Milestone3]


def get_next_date(milestones: Milestones):
    next_date = None

    for milestone in milestones:
        candidate = milestone.get_next_date(PARAMS["frequency"])
        if not next_date or candidate < next_date:
            next_date = candidate

    return next_date


def is_switch_to_revision_required(milestones: Milestones, source: Source, date):
    for milestone in milestones:
        if not milestone.has_log_for_date(source, date):
            return True
    return False


def update_milestones_for_revision(
        source: Source, milestones: Milestones, revision, use_current_revision):
    for milestone in milestones:
        rev_date = source.get_revision_date(revision, use_current_revision)
        milestone_last_date = milestone.get_last_date()
        if milestone_last_date and rev_date <= milestone_last_date:
            print(f"   - {milestone.name}: Skipping (Already collected)")
            continue
        result = milestone.collect_data(source, rev_date, revision)
        if result is None:
            print(f"   - {milestone.name}: Skipping (User aborted)")
            continue

        (progress_entry, snapshot) = result
        milestone.append_progress_entry(progress_entry)
        if PARAMS["dry_run"]:
            print(f"   - {milestone.name}: Not writing (dry run)")
        else:
            print(f"   - {milestone.name}: Writing")
            milestone.save_progress()
            milestone.save_snapshot(snapshot)


def main(use_current_revision, source: Source, milestones: Milestones):
    start_revision = source.get_current_revision()
    print(f"Your current revision is: {start_revision}")

    any_update_happened = False

    if use_current_revision:
        update_milestones_for_revision(
            source, milestones, start_revision, True)
        any_update_happened = True
    else:
        next_date = get_next_date(milestones)
        print(f"The first date we need to collect data for is: {next_date}")
        current_revision = None

        while True:
            next_revision = source.pick_next_revision(next_date)
            if next_revision == current_revision:
                break
            next_rev_date = source.get_revision_date(next_revision, False)

            if not next_date or next_rev_date < next_date:
                print(
                    f"But the latest available revision is {next_revision} ({next_rev_date})")
                response = input("Do you want to collect date for it (Y/N):")
                if response.lower() != "y":
                    break

            print(f"\nSelected revision: {next_revision} ({next_rev_date})")
            if is_switch_to_revision_required(milestones, source, next_rev_date):
                print(f" - Updating to revision")
                source.switch_to_revision(next_revision)
            current_revision = next_revision

            print(f" - Collecting data")
            any_update_happened = True
            update_milestones_for_revision(
                source, milestones, current_revision, False)
            next_date += PARAMS["frequency"]

        end_revision = source.get_current_revision()
        if start_revision != end_revision:
            print(f"Switching back to start revision: {start_revision}.")
            source.switch_to_revision(start_revision)

    if not any_update_happened:
        print("Could not find a revision for the next data update!")
    else:
        print("DONE!")


def is_file_writable(path, f):
    if os.path.exists(os.path.join(path, f)):
        return os.access(os.path.join(path, f), os.W_OK)
    return os.access(path, os.W_OK)


def verify_mc_path(parser, mc_path):
    if not os.access(mc_path, os.R_OK):
        parser.error(f"{mc_path} path is not readable!")


def verify_milestone_paths(
        parser: argparse.ArgumentParser, gh_pages_data_path: str, milestone_name: str):
    data_path = os.path.join(gh_pages_data_path, milestone_name)

    if not is_file_writable(data_path, "progress.json"):
        parser.error(
            f"{os.path.join(data_path, 'progress.json')} path is not writable!")
    if not is_file_writable(data_path, "snapshot.json"):
        parser.error(
            f"{os.path.join(data_path, 'snapshot.json')} path is not writable!")


def set_milestones(parser: argparse.ArgumentParser, args):
    milestone_args = args.milestone

    result: Milestones = []
    if "M1" in milestone_args or "all" in milestone_args:
        verify_milestone_paths(parser, args.gh_pages_data, "M1")
        result.append(Milestone1(args.gh_pages_data))
    if "M2" in milestone_args or "all" in milestone_args:
        verify_milestone_paths(parser, args.gh_pages_data, "M2")
        result.append(Milestone2(args.gh_pages_data))
    if "M3" in milestone_args or "all" in milestone_args:
        verify_milestone_paths(parser, args.gh_pages_data, "M3")
        result.append(Milestone3(args.gh_pages_data))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Aggregate data for arewefluentyet.com')
    parser.add_argument('-m', '--milestone',
                        required=True,
                        action='append',
                        choices=['M1', 'M2', 'M3', 'all'],
                        help='Comma-separated list of milestones to accumulate')
    parser.add_argument('--use-current-revision',
                        action='store_true',
                        help='If set, the script will collect data based on the current revision of mozilla-central.')
    parser.add_argument('--dry-run',
                        action='store_true',
                        help='If set, no data is written to files.')
    parser.add_argument('--mc',
                        required=True,
                        metavar='../mozilla-unified',
                        help='Path to mozilla-central clone')
    parser.add_argument('--gh-pages-data',
                        required=True,
                        metavar='../awfy/gh-pages/data',
                        help='Path to a data directory of a arewefluentyet.com/gh-pages clone')

    args = parser.parse_args()

    milestones = set_milestones(parser, args)

    verify_mc_path(parser, args.mc)
    source = Source(args.mc)

    PARAMS["dry_run"] = args.dry_run

    main(args.use_current_revision, source, milestones)
