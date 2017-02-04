#!/usr/bin/env python

import schedule
import config
import threading
import time
import datetime
import utils


class HumidexData(object):
    def __init__(self, indoor_data, outdoor_data):
        self.indoor_data = indoor_data
        self.outdoor_data = outdoor_data
        self.timestamp = datetime.datetime.now()

    def __str__(self):
        return "%s -> in:%s out:%s" % (
            str(self.timestamp), str(self.indoor_data), str(self.outdoor_data))

    def to_csv(self):
        return "%s,%s,%s,%s,%s" % (
            str(self.timestamp),
            str(self.indoor_data[0]),
            str(self.indoor_data[1]),
            str(self.outdoor_data[0]),
            str(self.outdoor_data[1])
        )


class HumidexUpdator(threading.Thread):
    def __init__(self, slo):
        threading.Thread.__init__(self)
        self.daemon = True
        schedule.every(
            config.INTERVAL_GET_HUMIDEX_FROM_SENSOR_MIN).minutes.do(
                slo.fetch_current_humidex_from_sensors)
        schedule.every(
            config.INTERVAL_SQUEEZE_HUMID_FROM_SHALLOW_CACHE_H).hours.do(
                slo.squeeze_shallow_cache_to_avg)
        schedule.every(
            config.INTERVAL_FLUSH_CACHE_TO_DB_H).hours.do(
                slo.flush_cache_to_db
            )
        self.start()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(config.INTERVAL_HUMIDEX_UPDATOR_SCHEDULER_SLEEP_S)


class HumidexSLO(object):
    def __init__(self, humidexDevicesFacade, humidexDb):
        self.updator = HumidexUpdator(self)
        self.humidex_devices_facade = humidexDevicesFacade
        self.humidex_db = humidexDb
        self.avg_cache = []
        self.shallow_cache = []
        self.lock = threading.RLock()
        self.once_flushed = False
        utils.execute_async(self.fetch_current_humidex_from_sensors)

    def get_last(self):
        # TODO: lock needed relly?
        with self.lock:
            if len(self.shallow_cache) > 0:
                return self.shallow_cache[-1]
            elif len(self.avg_cache) > 0:
                return self.avg_cache[-1]
            return None

    def fetch_current_humidex_from_sensors(self):
        data_indoor = self.humidex_devices_facade.get_humidex_indoor()
        data_outdoor = self.humidex_devices_facade.get_humidex_outdoor()
        with self.lock:
            self.shallow_cache.append(
                HumidexData(
                    indoor_data=data_indoor, outdoor_data=data_outdoor))
        # self.print_shallow()

    # @utils.timed
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
                del self.shallow_cache[:]
        # self.print_avg_cache()

    # @utils.timed
    def flush_cache_to_db(self):
        with self.lock:
            to_write = self.avg_cache[1:] \
                if self.once_flushed else self.avg_cache[:]  # copy
            print(str(self.avg_cache))
            print(str(to_write))
            self.humidex_db.append_entries(to_write)
            if len(self.avg_cache) > 0:
                self.avg_cache[0] = self.avg_cache[-1]
            self.avg_cache[1:] = []
            self.once_flushed = True

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
