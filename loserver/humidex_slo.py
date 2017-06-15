#!/usr/bin/env python

import config
import threading
import datetime
import utils
from multiprocessing.pool import ThreadPool


class HumidexData(object):  # TODO: move to separated module
    def __init__(self, indoor_data=None, outdoor_data=None, csv=None):
        if csv:
            entries = csv.split(",")
            if len(entries) != 5:
                raise Exception("Wrong format for given csv " + str(csv))
            self.timestamp = datetime.datetime.strptime(
                entries[0], "%Y-%m-%d %H:%M:%S.%f")
            self.indoor_data = (float(entries[1]), float(entries[2]))
            self.outdoor_data = (float(entries[3]), float(entries[4]))
        else:
            self.indoor_data = indoor_data
            self.outdoor_data = outdoor_data
            self.timestamp = datetime.datetime.now()
        self.init_states()

    def __str__(self):
        return "%s -> in:%s out:%s" % (
            str(self.timestamp), str(self.indoor_data), str(self.outdoor_data))

    def init_states(self):
        # add info if temp is mid - low - high etc
        pass

    def to_csv(self):
        return "%s,%s,%s,%s,%s" % (
            str(self.timestamp),
            str(self.indoor_data[0]),
            str(self.indoor_data[1]),
            str(self.outdoor_data[0]),
            str(self.outdoor_data[1])
        )

    def to_json(self):
        return {
            "out_temp": "%.1f" % self.outdoor_data[0],
            "out_humid": "%.f" % self.outdoor_data[1],
            "int_temp": "%.1f" % self.indoor_data[0],
            "int_humid": "%.0f" % self.indoor_data[1],
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M'),
            "int_humid_ok": self.is_humid_ok(self.indoor_data[1])
        }

    def is_humid_ok(self, humidity):
        return (humidity >= 40.0 and humidity <= 90.0)


class HumidexSLO(object):
    def __init__(self, humidexDevicesFacade, humidexDb):
        self.workers_pool = ThreadPool(processes=2)
        self.humidex_devices_facade = humidexDevicesFacade
        self.humidex_db = humidexDb
        self.avg_cache = []
        self.shallow_cache = []
        self.lock = threading.RLock()
        self.once_flushed = False
        self.fetch_current_humidex_from_sensors()

    def get_last(self):
        if len(self.shallow_cache) > 0:
            return self.shallow_cache[-1]
        elif len(self.avg_cache) > 0:
            return self.avg_cache[-1]
        return None

    def get_last_24h(self):
        max_last_entries_number = \
            int(24 / config.INTERVAL_SQUEEZE_HUMID_FROM_SHALLOW_CACHE_H)

        shallow = self.shallow_cache
        shallow.reverse()
        avg = self.avg_cache
        avg.reverse()
        local_and_db = shallow + avg \
            + self.humidex_db.read_db(max_last_entries_number)
        data_24h_min = datetime.datetime.now() - datetime.timedelta(hours=24)
        return filter(lambda x: x.timestamp > data_24h_min, local_and_db)

    def fetch_current_humidex_from_sensors(self):
        try:
            async_out_data = self.workers_pool.apply_async(
                self.humidex_devices_facade.get_humidex_outdoor, ())
            async_in_data = self.workers_pool.apply_async(
                self.humidex_devices_facade.get_humidex_indoor, ())
            data_outdoor = async_out_data.get()
            data_indoor = async_in_data.get()
            with self.lock:
                self.shallow_cache.append(
                    HumidexData(
                        indoor_data=data_indoor, outdoor_data=data_outdoor))
        except Exception as e:
            print("Error during fetch_current_humidex_from_sensors %s" % str(e))
        #self.print_shallow()

    @utils.timed
    def squeeze_shallow_cache_to_avg(self):
        with self.lock:
            if len(self.shallow_cache) > 0:
                out_temp_avg = utils.avg(
                    [x.outdoor_data[0] for x in self.shallow_cache])
                out_humi_avg = utils.avg(
                    [x.outdoor_data[1] for x in self.shallow_cache])
                in_temp_avg = utils.avg(
                    [x.indoor_data[0] for x in self.shallow_cache])
                in_humi_avg = utils.avg(
                    [x.indoor_data[1] for x in self.shallow_cache])
                avg = HumidexData(
                    (in_temp_avg, in_humi_avg), (out_temp_avg, out_humi_avg))
                avg.timestamp = self.shallow_cache[-1].timestamp
                self.avg_cache.append(avg)
                self.shallow_cache = []
        #self.print_avg_cache()

    @utils.timed
    def flush_cache_to_db(self):
        with self.lock:
            if len(self.avg_cache) > 0:
                to_write = self.avg_cache[1:] \
                    if self.once_flushed else self.avg_cache[:]
                self.humidex_db.append_entries(to_write)
                self.once_flushed = True
                last_el = self.avg_cache[-1]
                self.avg_cache = [last_el]

    def print_shallow(self):
        print("shallow->")
        with self.lock:
            for el in self.shallow_cache:
                print(str(el))

    def print_avg_cache(self):
        print("avg->")
        with self.lock:
            for el in self.avg_cache:
                print(str(el))


def test():
    HumidexSLO()


if __name__ == '__main__':
    test()
