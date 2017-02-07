#!/usr/bin/env python
from subprocess import check_output
from utils import timed
from config import ADAFRUIT_LIB_PATH
import traceback

TEMPERATURE_OUTDOOR_PIN = 6
TEMPERATURE_INDOOR_PIN = 12


class HumidexDevicesFacade(object):
    def __get_temp_and_humidity__(self, outdoor=False):
        pin = TEMPERATURE_OUTDOOR_PIN if outdoor else TEMPERATURE_INDOOR_PIN

        for _ in range(3):
            try:
                out = check_output([ADAFRUIT_LIB_PATH, "2302", str(pin)])
                break
            except:
                print(str(traceback.format_exc()))
        temp_str, humid_str = out.split()
        temp_str = temp_str.split("=")[1][:-1]
        humid_str = humid_str.split("=")[1][:-1]
        return (float(temp_str), float(humid_str))

    def humidex_n_times(self, get_data_function, n=3, outdoor=False):
        results_temp = []
        results_humid = []
        for _ in range(n):
            data = get_data_function(outdoor)
            results_humid.append(data[1])
            results_temp.append(data[0])
        results_temp.sort()
        results_humid.sort()
        return (results_temp[n/2], results_humid[n/2])

    @timed
    def get_humidex_indoor(self):
        return self.humidex_n_times(
            get_data_function=self.__get_temp_and_humidity__)

    @timed
    def get_humidex_outdoor(self):
        return self.humidex_n_times(
            get_data_function=self.__get_temp_and_humidity__, outdoor=True)
