#!/usr/bin/env python

from humidex_slo import HumidexSLO
from devices import HumidexDevicesFacade
import flask
from flask import Flask
app = Flask(__name__)

humidexDevicesFacade = HumidexDevicesFacade()
humidex = HumidexSLO(humidexDevicesFacade)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/temp')
def temp():
    data = humidex.get_last()
    if not data:
        return "No data"
    response = {
        "out_temp": str(data.outdoor_data[0]),
        "out_humid": str(data.outdoor_data[1]),
        "in_temp": str(data.indoor_data[0]),
        "int_humid": str(data.indoor_data[1]),
        "timestamp": str(data.timestamp)
    }
    return flask.jsonify(response)


app.run(debug=True, host='0.0.0.0', port=81)
