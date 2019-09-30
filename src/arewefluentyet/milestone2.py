import os
import re
import subprocess
from datetime import date
from milestone import Milestone


class Milestone2(Milestone):
    name = "M2"
    start_date = date(2019, 8, 25)
    log_dir = "startup_log"
    bookmark = "collect-startup-entries"

    def get_log_path(self, source, date):
        log_name = "data-{}.txt".format(date.strftime("%Y%m%d"))
        log_path = os.path.join(source.path, self.log_dir, log_name)
        return log_path

    def has_log_for_date(self, source, date):
        log_path = self.get_log_path(source, date)
        return os.path.exists(log_path)

    def get_data(self, source, date, revision):
        if not self.has_log_for_date(source, date):
            response = input(f"About to attempt to apply the `collect-startup-entries` onto {revision} (Y/N): ")
            if response.lower() != "y":
                return None
            source.rebase_bookmark(revision, self.bookmark)
            source.switch_to_revision(self.bookmark)

            response = input("About to build Firefox with the `collect-startup-entries` (Y/N): ")
            if response.lower() != "y":
                return None

            print(f"Building Firefox with `collect-startup-entries`. You can see the progress via `tail -f firefox-build-log.txt`.")
            source.build_firefox()

            response = input("About to launch Firefox with `collect-startup-entries` (Y/N): ")
            if response.lower() != "y":
                return None

            self.collect_log(source, date, revision)

        log_path = self.get_log_path(source, date)
        raw_data = open(log_path).read()
        (entries, progress) = self.extract_progress(raw_data)
        return (entries, progress)

    def extract_progress(self, raw_data):
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

        matches = re.finditer("== Entry ==(.*?)== Entry End ==",
                              raw_data, re.DOTALL | re.MULTILINE)
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
                entry["stack"] = self.parse_stack(entry["stack"])

            if entry["type"] == "dtd":
                context = self.find_context(contexts, match.start())
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

    def parse_stack(self, stack):
        result = []

        for line in stack.split("\n"):
            if len(line.strip()) == 0:
                continue
            match = re.match("([0-9]+) (.*?) \[\"([^\"]+)\":([0-9]+):([0-9]+)]", line)
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

    def find_context(self, contexts, pos):
        for context in contexts:
            if context["from"] <= pos and (context["to"] >= pos or context["to"] is None):
                return context
        return None

    def collect_log(self, source, date, revision):
        log_path = self.get_log_path(source, date)
        cmd = os.path.join(source.path, "mach")
        dir_name = os.path.dirname(log_path)
        os.makedirs(dir_name, exist_ok=True)

        with open(log_path, "w") as fp:
            fp.write(f"revision: {revision}\n")
            fp.write(f"date: {date}\n")
            subprocess.run(
                [cmd, "run", "--temp-profile"], stdout=fp, check=True)
