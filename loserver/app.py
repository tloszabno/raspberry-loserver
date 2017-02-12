#!/usr/bin/env python

from humidex_slo import HumidexSLO
from humidex_db import HumidexDB
from humidex_web import HumidexWeb
from flask import Flask, send_from_directory
from web import Response
import flask
import sys
app = Flask(__name__, static_folder='web')

humidex = None


@app.route('/humidex_info')
def get_humidex_info():
    data = humidex.get_humidex_info()
    if not data:
        return flask.jsonify(Response(ok=False, errors=['No data found']))
    return flask.jsonify(Response(data=data.to_json()))


# @app.route('/temp_24h')
# def last_temp_24h():
#     data = humidex.get_last_24h()
#     if not data:
#         return "No data"
#     return flask.jsonify([x.to_json() for x in data])


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
    humidexSLO = HumidexSLO(humidexDevicesFacade, humidexDB)
    humidex = HumidexWeb(humidexSLO)


if __name__ == '__main__':
    use_mocks = len(sys.argv) > 1 and sys.argv[1] == "--mocked"
    init(use_mocks)
    app.run(host='0.0.0.0', port=81, debug=True)
