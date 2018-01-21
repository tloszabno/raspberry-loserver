#!/usr/bin/env python
import threading
import time
import traceback
from multiprocessing.pool import ThreadPool
from subprocess import check_output

import RPi.GPIO as gpio
import requests

import properties
from config import ADAFRUIT_LIB_PATH
from config import SEEP_TIME_BEFORE_MEASUREMENT_OF_PM_M
from utils import timed

TEMPERATURE_OUTDOOR_PIN = 6
TEMPERATURE_INDOOR_PIN = 12

PM_SENSOR_BOARD_PIN = 38
PM_SENSOR_PORT = '/dev/ttyUSB0'


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
        return (results_temp[n / 2], results_humid[n / 2])

    @timed
    def get_humidex_indoor(self):
        return self.humidex_n_times(
            get_data_function=self.__get_temp_and_humidity__)

    @timed
    def get_humidex_outdoor(self):
        return self.humidex_n_times(
            get_data_function=self.__get_temp_and_humidity__, outdoor=True)


class PMSensorDeviceFacade(object):
    def __init__(self):
        self.workers_pool = ThreadPool(processes=2)
        self.inside = (0.0, 0.0)
        self.outside = (0.0, 0.0)
        self.lock = threading.RLock()
        self.__setup_gpio__()

    def update_reads(self):
        self.workers_pool.apply_async(self.__read_pm_sensor__, ())

    def get(self):
        return self.inside, self.outside

    def __read_pm_sensor__(self):
        gpio.output(PM_SENSOR_BOARD_PIN, True)  # turn on pm sensor
        time.sleep(SEEP_TIME_BEFORE_MEASUREMENT_OF_PM_M)
        t = serial.Serial(PM_SENSOR_PORT, 9600)
        from_sensor = None
        for i in range(3):  # take 3 reads before save
            from_sensor = getPM(t)
            time.sleep(1)
        from_airly = getFromAirly()
        with self.lock:
            self.inside = from_sensor
            self.outside = from_airly

    def __setup_gpio__(self):
        gpio.setmode(gpio.BOARD)
        gpio.setup(PM_SENSOR_BOARD_PIN, gpio.OUT)
        gpio.output(PM_SENSOR_BOARD_PIN, False)


def getPM(terminal):
    def hexShow(argv):
        result = ''
        hLen = len(argv)
        for i in range(hLen):
            hvol = ord(argv[i])
            hhex = '%02x' % hvol
            result += hhex + ' '

    terminal.flushInput()
    retstr = terminal.read(10)
    hexShow(retstr)
    if len(retstr) == 10:
        if (retstr[0] == b"\xaa" and retstr[1] == b'\xc0'):
            checksum = 0
            for i in range(6):
                checksum = checksum + ord(retstr[2 + i])
            if checksum % 256 == ord(retstr[8]):
                pm25 = ord(retstr[2]) + ord(retstr[3]) * 256
                pm10 = ord(retstr[4]) + ord(retstr[5]) * 256
                return pm10 / 10.0, pm25 / 10.0
    return (0.0, 0.0)


def getFromAirly():
    headers = {'apikey': properties.tokens['airly'], 'Accept': 'application/json'}
    response = requests.get('https://airapi.airly.eu/v1/sensor/measurements?sensorId=215', headers=headers).json()
    current = response['currentMeasurements']
    pm25 = current['pm25']
    pm10 = current['pm10']
    return pm10, pm25
