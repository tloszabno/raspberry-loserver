import threading
import time

import schedule

import config


class Updator(threading.Thread):
    def __init__(self, humidex_slo, wunderlist_slo, pm_facade):
        threading.Thread.__init__(self)
        self.daemon = True
        schedule.every(
            config.INTERVAL_GET_HUMIDEX_FROM_SENSOR_MIN).minutes.do(
            humidex_slo.fetch_current_humidex_from_sensors)
        schedule.every(
            config.INTERVAL_SQUEEZE_HUMID_FROM_SHALLOW_CACHE_H).hours.do(
            humidex_slo.squeeze_shallow_cache_to_avg)
        schedule.every(
            config.INTERVAL_FLUSH_CACHE_TO_DB_H).hours.do(
            humidex_slo.flush_cache_to_db
        )
        schedule.every(
            config.INTERVAL_REFRESH_WUNDERLIST_TASKS_MIN).minutes.do(
            wunderlist_slo.update_cache
        )
        schedule.every(
            config.INTERVAL_TO_REFRESH_PM_SENSORS_M).minutes.do(pm_facade.update_reads)
        self.start()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(config.INTERVAL_HUMIDEX_UPDATOR_SCHEDULER_SLEEP_S)
