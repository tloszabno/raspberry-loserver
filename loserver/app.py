#!/usr/bin/env python

from humidex_slo import HumidexSLO
from humidex_db import HumidexDB
from humidex_web import HumidexWeb
from day_info_web import DayInfoWeb
from wunderlist_facade import WunderFacade
from wunderlist_slo import WunderSLO
from wunderlist_web import WunderListWeb
from updator import Updator
from flask import Flask, send_from_directory
from web import Response
import flask
import sys
app = Flask(__name__, static_folder='web')

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

humidex = None
day_info = None
updator = None
wunder_web = None


@app.route('/humidex_info')
def get_humidex_info():
    data = humidex.get_humidex_info()
    if not data:
        return flask.jsonify(Response(ok=False, errors=['No data found']))
    return flask.jsonify(Response(data=data.to_json()))


@app.route('/day_info')
def get_day_info():
    return flask.jsonify(Response(data=day_info.get_day_info()))


@app.route('/wunderlist_todo_dom')
def get_wunderlist_todo_dom():
    return flask.jsonify(Response(data=wunder_web.get_todo_dom_tasks()))


@app.route('/wunderlist_today')
def get_wunderlist_today():
    return flask.jsonify(Response(data=wunder_web.get_today_tasks()))


@app.route("/")
def hello():
    return app.send_static_file('index.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('web/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('web/css', path)


def init(use_mocks):
    global humidex, day_info, updator, wunder_web
    if humidex is not None:
        return
    humidexDevicesFacade = None
    pm_facade = None
    if not use_mocks:
        from devices import HumidexDevicesFacade
        humidexDevicesFacade = HumidexDevicesFacade()
        from devices import PMSensorDeviceFacade
        pm_facade = PMSensorDeviceFacade()
    else:
        print("Using mocks")
        from devices_mocks import HumidexDevicesFacadeMock
        humidexDevicesFacade = HumidexDevicesFacadeMock()
        from devices_mocks import  PMSensorDeviceFacadeMock
        pm_facade = PMSensorDeviceFacadeMock()

    humidexDB = HumidexDB()
    humidexSLO = HumidexSLO(humidexDevicesFacade, pm_facade, humidexDB)
    wunderFacade = WunderFacade()
    wunder_slo = WunderSLO(wunderFacade)
    wunder_web = WunderListWeb(wunder_slo)
    humidex = HumidexWeb(humidexSLO)
    day_info = DayInfoWeb(wunder_slo)
    updator = Updator(humidexSLO, wunder_slo, pm_facade)


if __name__ == '__main__':
    use_mocks = len(sys.argv) > 1 and sys.argv[1] == "--mocked"
    init(use_mocks)
    app.run(host='0.0.0.0', port=81, debug=use_mocks)
