from bus_info import BusInfo
from data import stop_aliases
from flask import Blueprint, render_template
from flask_ask import Ask, statement
from difflib import get_close_matches

class InvalidStop(Exception):
	def __init__(self, message):
		super(Exception, self).__init__(message)

blueprint = Blueprint("MBus_blueprint", __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

@ask.launch
def launch():
	return statement("Hello, welcome to M-Bus Voice.")

bus_info = BusInfo()

# Take the user's spoken stop name and figure out which stop 
# id(s) they are referring to and return it/them as a list.
def clarifyStopName(user_phrase):
	# Use system level aliases and the stops given by the API and 
	# see if the user was referring to one of those stops
	stops_by_name = {stop.name.lower(): [stop_id] for stop_id, stop in bus_info.stops.items()}
	stops_by_name.update(stop_aliases)
	user_phrase = user_phrase.lower()
	if user_phrase in stops_by_name:
		return user_phrase, stops_by_name[user_phrase]

	# Difflib for user level aliases
	# Need to get the user level aliases from the database
	user_aliases = {}

	# Difflib for system level aliases and API stop names
	close_matches = get_close_matches(user_phrase, stops_by_name.keys())
	if close_matches:
		name = close_matches[0]
		return name, stops_by_name[name]

	# Raise an error if the user_phrase couldn't be clarified
	raise InvalidStop(user_phrase+" is not a valid stop name")

@ask.intent("GetNextBuses", 
	default={
		"StartStop": None,
		"EndStop": None,
		"RouteName": None,
		"NumBuses": 1
	})
def getNextBuses(StartStop, EndStop, RouteName, NumBuses):
	# If parameters are None, get user values from the database
	# If the user hasn't specified default values raise an error
	if not StartStop:
		StartStop = "baits ii - inbound"
	if not EndStop:
		EndStop = "central campus transit center: cc little"
	if not RouteName:
		RouteName = "bursley-baits"

	# Try to understand which stop the user is talking about
	RouteName = RouteName.lower()
	try:
		StartStop, start_stops = clarifyStopName(StartStop)
		EndStop, end_stops = clarifyStopName(EndStop)
	except InvalidStop as e:
		return statement(e.message)

	# This is where we need to connect the start stops to the
	# end stops via a route
	origin_etas = []
	for start_stop in start_stops:
		stop_etas = bus_info.get_eta(start_stop)
		for stop_eta in stop_etas:
			if stop_eta.route in bus_info.routes:
				origin_etas.append(stop_eta)

	etas = []
	for eta in bus_info.sort_etas(origin_etas):
		if set(bus_info.routes[eta.route].stops).intersection(set(end_stops)):
			etas.append(eta)

	if not etas:
		return statement("No buses are currently going from "+StartStop+" to "+EndStop)

	options = {
		"origin": StartStop,
		"destination": EndStop
	}
	NumBuses = int(NumBuses)
	if NumBuses == 1:
		template = "GetNextBus"
		eta = etas[0]
		options.update({
			"route": bus_info.routes[eta.route].name,
			"minutes": eta.time
		})
	else:
		template = "GetNextBuses"
		message = ""
		count = 0
		for eta in etas:
			message += "a "+bus_info.routes[eta.route].name+" bus in "+str(eta.time)+" "+("minute" if eta.time == 1 else "minutes")
			count += 1
			if count == NumBuses:
				break
			message += ", "
			if count == NumBuses - 1 or count == len(etas) - 1:
				message += "and "

		options.update({
			"busInfo": message
		})
	text = render_template(template, **options)
	return statement(text).simple_card(template, text)

@ask.intent("SetFavorite")
def setFavorite(StopName):
	return statement("Not Implemented")

@ask.intent("AssistedSetup")
def assistedSetup():
	return statement("Not Implemented")
