from bus_info import BusInfo
from flask import Blueprint, render_template
from flask_ask import Ask, statement

blueprint = Blueprint("MBus_blueprint", __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

@ask.intent("GetNextBusesForStop")
def getNextBusesForStop(StopID):
	bus_info = BusInfo([100, 597, 594, 596, 633])
	eta = bus_info.get_eta(StopID).values()[0]
	options = {
		"stopid": StopID,
		"minutes": eta.time,
		"busline": bus_info.routes[eta.route].name
	}
	text = render_template('GetNextBusesForStop', **options)
	return statement(text).simple_card('GetNextBusesForStop', text)

@ask.launch
def launch():
	return statement("Hello, welcome to M-Bus Voice.")
