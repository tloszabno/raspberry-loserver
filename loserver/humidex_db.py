#!/usr/bin/env python
import config


class HumidexDB(object):
    def __init__(self):
        pass

    def append_entries(self, to_write):
        with open(config.DB_FILE_PATH, "a+") as f:
            for entry in to_write:
                f.write(entry.to_csv())
                f.write('\n')
