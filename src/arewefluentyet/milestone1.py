import os
import re
from collections import defaultdict
from datetime import date
from milestone import Milestone
from functools import partial


class Milestone1(Milestone):
    name = "M1"
    start_date = date(2019, 3, 24)
    main_file = "./browser/base/content/browser.xhtml"

    def get_data(self, source, date, revision):
        entries = []
        self.matches_in_file(self.main_file, entries, source.path)

        progress = defaultdict(int)

        for entry in entries:
            progress[entry["type"]] += 1

        return (entries, progress)

    def load_include(self, path, match=None):
        if match is not None:
            path = os.path.join(path, match[1])
        raw_data = open(path).read()

        new_dir = os.path.dirname(path)

        raw_data = re.sub('#include (.*)', partial(self.load_include, new_dir),
                          raw_data)
        return raw_data

    def matches_in_file(self, path, entries, mc_path):
        full_path = os.path.join(mc_path, path)
        raw_data = self.load_include(full_path)

        re_dtd = re.compile("&([a-zA-Z][^;]+);")
        matches = re_dtd.findall(raw_data)
        for match in matches:
            entries.append({"type": "dtd", "id": match})

        re_ftl = re.compile("data(?:-lazy)?-l10n-id=\"([^\"]+)\"")
        matches = re_ftl.findall(raw_data)
        entries.extend(({"type": "ftl", "id": match} for match in matches))
