#!/usr/bin/env python

from devices import get_humidex_indoor
from devices import get_humidex_outdoor
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
        self.start()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(config.INTERVAL_HUMIDEX_UPDATOR_SCHEDULER_SLEEP_S)


class HumidexSLO(object):
    def __init__(self):
        self.updator = HumidexUpdator(self)
        self.avg_cache = []
        self.shallow_cache = []
        self.lock = threading.RLock()
        self.fetch_current_humidex_from_sensors()
        self.updator.join()

    def fetch_current_humidex_from_sensors(self):
        with self.lock:
            data_indoor = get_humidex_indoor()
            data_outdoor = get_humidex_outdoor()
            self.shallow_cache.append(
                HumidexData(
                    indoor_data=data_indoor, outdoor_data=data_outdoor))
        self.print_shallow()

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
        self.print_avg_cache()

    def print_shallow(self):
        with self.lock:
            for el in self.shallow_cache:
                print(str(el))

    def print_avg_cache(self):
        with self.lock:
            for el in self.avg_cache:
                print(str(el))


def test():
    h = HumidexSLO()


if __name__ == '__main__':
    test()
