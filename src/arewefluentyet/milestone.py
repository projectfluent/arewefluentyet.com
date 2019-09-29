import os
import json
from datetime import date


def parse_date(input):
    return date(*(int(s) for s in input.split("-")))


class Milestone:
    name = None
    start_date = None

    def __init__(self, data_path):
        self.data_path = os.path.join(data_path, self.name)
        self.progress_data = None

    def append_progress_entry(self, progress_entry):
        self.get_progress_data().append(progress_entry)

    def get_progress_data(self):
        if self.progress_data is None:
            path = os.path.join(self.data_path, "progress.json")

            if os.path.exists(path):
                self.progress_data = json.load(open(path))
            else:
                self.progress_data = []

        return self.progress_data

    def has_log_for_date(self, source, date):
        """
        This method can be overloaded by subclasses which can cache log for a given date.

        Milestone2 does it to save us from having to rebuild/relaunch to generate the log.
        """
        return False

    def get_data(self, date, revision):
        raise NotImplementedError

    def collect_data(self, source, date, revision):
        result = self.get_data(source, date, revision)
        if result is None:
            return None

        (entries, progress) = result

        snapshot = {"date": str(date), "revision": revision, "data": entries}

        progress_entry = {
            "data": progress,
            "date": snapshot["date"],
            "revision": snapshot["revision"],
        }

        return (progress_entry, snapshot)

    def get_next_date(self, frequency):
        progress_data = self.get_progress_data()
        if len(progress_data) > 0:
            return parse_date(progress_data[-1]["date"]) + frequency
        else:
            return self.start_date

    def get_last_date(self):
        progress_data = self.get_progress_data()
        if len(progress_data) > 0:
            return parse_date(progress_data[-1]["date"])
        else:
            return None

    def save_progress(self):
        json.dump(
            self.progress_data,
            open(os.path.join(self.data_path, "progress.json"), "w"),
            indent=0,
            separators=(",", ": "),
            sort_keys=True,
        )

    def save_snapshot(self, snapshot):
        json.dump(
            snapshot,
            open(os.path.join(self.data_path, "snapshot.json"), "w"),
            indent=0,
        )
