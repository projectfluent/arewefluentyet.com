import subprocess
import os
from datetime import date


def parse_date(input):
    return date(*(int(s) for s in input.split("-")))


class Source:
    def __init__(self, path: str):
        self.path = path
        self.current_revision = None

    def get_current_revision(self):
        if not self.current_revision:
            result = subprocess.run([
                "hg", "id", "--cwd", self.path, "-T{id}"
            ], check=True, capture_output=True, encoding="ascii")
            self.current_revision = result.stdout
        return self.current_revision

    def pick_next_revision(self, next_date):
        result = subprocess.run([
            "hg", "log",
            "--cwd", self.path,
            "-l", "1",
            "-T", "{node}",
            "-r",
            f"reverse(pushhead() and pushdate('< {next_date}') and ::central)"
        ], check=True, capture_output=True, encoding="ascii")
        return result.stdout

    def get_revision_date(self, rev, use_current_revision):
        if use_current_revision:
            result = subprocess.run([
                "hg", "id", "--cwd", self.path,
                "-r", rev, "-T", "{date|shortdate}"
            ], check=True, capture_output=True, encoding="ascii")
        else:
            result = subprocess.run([
                "hg", "id", "--cwd", self.path,
                "-r", rev, "-T", "{pushdate|shortdate}"
            ], check=True, capture_output=True, encoding="ascii")

        return parse_date(result.stdout)

    def switch_to_revision(self, rev):
        if rev == self.current_revision:
            return

        subprocess.run([
            "hg", "status", "--cwd", self.path, "-mard"
        ], check=True)

        subprocess.run([
            "hg", "update", "--cwd", self.path, "-c", "-r", rev
        ], check=True)
        self.current_revision = rev

    def get_bookmark_parent(self, bookmark):
        result = subprocess.run([
            "hg", "log",
            "--cwd", self.path,
            "-r", bookmark,
            "-T", "{p1.node}",
        ], check=True, capture_output=True, encoding="ascii")

        return result.stdout

    def rebase_bookmark(self, revision, bookmark):
        parent = self.get_bookmark_parent(bookmark)
        if parent != revision:
            subprocess.run([
                "hg", "rebase", "--cwd", self.path,
                "-b", bookmark, "-d", revision
            ], check=True, stdout=subprocess.DEVNULL)

    def build_firefox(self):
        cmd = os.path.join(self.path, "mach")
        with open("firefox-build-log.txt", "w") as fp:
            subprocess.run([cmd, "build"], stdout=fp, check=True)
