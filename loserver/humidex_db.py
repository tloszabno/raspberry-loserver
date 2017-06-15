#!/usr/bin/env python
import config
import threading
from humidex_slo import HumidexData


class HumidexDB(object):
    def __init__(self):
        self.lock = threading.RLock()

    def append_entries(self, to_write):
        with self.lock:
            with open(config.DB_FILE_PATH, "a+") as f:
                for entry in to_write:
                    e = entry.to_csv()
                    #print("Writing to db entry-> %s" % e)
                    f.write(e)
                    f.write('\n')

    def read_db(self, max_last_entries):
        with self.lock:
            lines = []
            with open(config.DB_FILE_PATH, "r") as f:
                lines = [x.strip() for x in f.readlines()]
            lines = lines[-max_last_entries:]
            lines.reverse()
            return [HumidexData(csv=line) for line in lines]
