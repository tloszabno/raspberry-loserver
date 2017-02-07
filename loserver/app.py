#!/usr/bin/env python

from humidex_slo import HumidexSLO
from humidex_db import HumidexDB
from flask import Flask
import flask
import sys
app = Flask(__name__)

humidex = None


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/temp')
def last_temp():
    data = humidex.get_last()
    if not data:
        return "No data"
    return flask.jsonify(data.to_json())


@app.route('/temp_24h')
def last_temp_24h():
    data = humidex.get_last_24h()
    if not data:
        return "No data"
    return flask.jsonify([x.to_json() for x in data])


def init(use_mocks):
    global humidex
    if humidex is not None:
        return
    humidexDevicesFacade = None
    if not use_mocks:
        from devices import HumidexDevicesFacade
        humidexDevicesFacade = HumidexDevicesFacade()
    else:
        print("Using mocks")
        from devices_mocks import HumidexDevicesFacadeMock
        humidexDevicesFacade = HumidexDevicesFacadeMock()

    humidexDB = HumidexDB()
    humidex = HumidexSLO(humidexDevicesFacade, humidexDB)


if __name__ == '__main__':
    use_mocks = len(sys.argv) > 1 and sys.argv[1] == "--mocked"
    init(use_mocks)
    app.run(host='0.0.0.0', port=81, debug=False)
