# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from compare_locales import mozpath
from compare_locales import paths
from compare_locales.paths import configparser
from compare_locales.paths import files
from compare_locales import parser


class Aggregator(object):
    def __init__(self, config_paths):
        self.config_paths = config_paths
        self.configs = []

    def load(self):
        p = configparser.TOMLParser()
        del self.configs[:]
        for path in self.config_paths:
            cfg = p.parse(path, env={"l10n_base": mozpath.abspath(".")})
            cfg.set_locales(["en-US"], True)
            self.configs.append(cfg)

    def gather(self):
        fls = files.ProjectFiles("en-US", self.configs)
        results = [{} for cfg in self.configs]
        for l10n_path, f, _, tests in fls:
            if "android-dtd" in tests:
                # ignore Android native strings
                continue
            try:
                p = parser.getParser(f)
            except UserWarning:
                continue
            p.readFile(f)
            string_count = len(list(p))
            for i, cfg in enumerate(self.configs):
                l10n_file = paths.File(l10n_path, mozpath.relpath(l10n_path, mozpath.abspath(".")), locale='en-US')
                if cfg.filter(l10n_file) != "ignore":
                    results[i][l10n_file.file] = string_count
        return results
