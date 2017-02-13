from bus_info import BusInfo
from flask import Blueprint, render_template
from flask_ask import Ask, statement

blueprint = Blueprint("MBus_blueprint", __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

@ask.launch
def launch():
	return statement("Hello, welcome to M-Bus Voice.")

@ask.intent("GetNextBusesForOrigin")
def getNextBusesForOrigin(StopName):
	# Try to understand which stop the user is talking about
	bus_info = BusInfo()
	stops_by_name = {stop.name.lower(): stop_id for stop_id, stop in bus_info.stops.items()}
	StopName = StopName.lower()
	if StopName in stops_by_name:
		stopID = stops_by_name[StopName]
	else:
		return statement("I don't know of the stop "+StopName)

	etas = bus_info.get_eta(stopID)
	if len(etas) == 0:
		return statement("No buses are currently coming to "+StopName)
		
	eta = etas.values()[0]
	options = {
		"stopName": StopName,
		"minutes": eta.time,
		"busLine": bus_info.routes[eta.route].name
	}
	text = render_template('GetNextBusesForOrigin', **options)
	return statement(text).simple_card('GetNextBusesForOrigin', text)

@ask.intent("GetNextBusesForDestination")
def getNextBusesForDestination(StopName):
	return statement("Not Implemented")

@ask.intent("SetFavorite")
def setFavorite(StopName):
	return statement("Not Implemented")

@ask.intent("AssistedSetup")
def assistedSetup():
	return statement("Not Implemented")
