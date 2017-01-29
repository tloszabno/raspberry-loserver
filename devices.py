#!/usr/bin/env python
from subprocess import check_output
from utils import timed

TEMPERATURE_OUTDOOR_PIN = 6
TEMPERATURE_INDOOR_PIN = 12
ADAFRUIT_LIB_PATH = "/home/osmc/libs/" + \
    "Adafruit_Python_DHT/examples/AdafruitDHT.py"


def __get_temp_and_humidity__(outdoor=False):
    pin = TEMPERATURE_OUTDOOR_PIN if outdoor else TEMPERATURE_INDOOR_PIN
    out = check_output([ADAFRUIT_LIB_PATH, "2302", str(pin)])
    temp_str, humid_str = out.split()
    temp_str = temp_str.split("=")[1][:-1]
    humid_str = humid_str.split("=")[1][:-1]
    return (float(temp_str), float(humid_str))


def humidex_n_times(get_data_function, n=3, outdoor=False):
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
def get_humidex_indoor():
    return humidex_n_times(get_data_function=__get_temp_and_humidity__)


@timed
def get_humidex_outdoor():
    return humidex_n_times(
        get_data_function=__get_temp_and_humidity__, outdoor=True)


def test():
    print("Temp and humidity outside = %s" % str(
        get_humidex_indoor()))
    print("Temp and humidity inside = %s" % str(
        get_humidex_outdoor()))


if __name__ == "__main__":
    test()
