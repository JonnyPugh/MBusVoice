from quarantine import *
from flask import Blueprint, render_template
from flask_ask import Ask, statement, session

blueprint = Blueprint("MBus_blueprint", __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

# Introduce the skill and demonstrate how to use it
@ask.launch
def launch():
	return statement("Hello, welcome to M-Bus Voice.")

# Get bus information based on a variety of different parameters
@ask.intent("GetNextBuses", 
	default={
		"StartStop": None,
		"EndStop": None,
		"RouteName": None,
		"NumBuses": 1
	})
def getNextBuses(StartStop, EndStop, RouteName, NumBuses):
	# Get user preferences from the database
	user_info = db.get_item(session.user.userId)
	template = "MissingFavorite"

	try:
		# Try to understand which stops the user is talking about
		if StartStop:
			StartStop, start_stops = shared.clarifyStopName(StartStop, user_info["origins"])
		else:
			start_stops = user_info["origins"].values()
			if not start_stops:
				text = render_template(template, stopType="starting", favoriteType="home")
				return statement(text).simple_card(template, text)
		if EndStop:
			EndStop, end_stops = shared.clarifyStopName(EndStop, user_info["destinations"])
		else:
			stopID = user_info["default_destination"]
			if stopID == -1:
				text = render_template(template, stopType="ending", favoriteType="destination")
				return statement(text).simple_card(template, text)
			end_stops = [stopID]
			EndStop = {stopid: alias for alias, stopid in user_info["destinations"].items()}[stopID]
	except shared.InvalidUserAlias as e:
		return statement(e.message)

	# If the origin and destination are the same, return an error message
	if set(start_stops) == set(end_stops):
		return statement("The starting stop "+EndStop+" cannot be the same as the destination")

	# Determine all valid etas based on the start and end stops
	etas = []
	for start_stop in start_stops:
		for stop_eta in bus_info.get_eta(start_stop):
			route = bus_info.routes[stop_eta.route]
			if not (RouteName and not get_close_matches(RouteName, [route.name])) and set(route.stops).intersection(set(end_stops)):
				# If the route of the eta is the not the specified 
				# route or if the route doesn't contain one of the 
				# destination stops, don't use it as a possible eta
				etas.append((stop_eta, start_stop))

	# If there are no valid etas, return an error message
	if not etas:
		template = "NoEtas"
		text = render_template(template, 
			route=RouteName if RouteName else "", 
			origin=StartStop if StartStop else "your home stops", 
			destination=EndStop)
		return statement(text).simple_card(template, text)

	# Sort the etas by how soon their bus will arrive at their origin stop
	etas = sorted(etas, key=lambda eta_info: eta_info[0].time)

	# Form the response and return it to the user
	options = {
		"destination": EndStop
	}
	NumBuses = int(NumBuses)
	if NumBuses == 1:
		template = "GetNextBus"
		eta_info = etas[0]
		eta = eta_info[0]
		stopID = eta_info[1]
		if not StartStop:
			StartStop = {stopid: alias for alias, stopid in user_info["origins"].items()}[stopID]	
		options.update({
			"origin": StartStop if len(start_stops) == 1 else bus_info.stops[stopID].name,
			"route": bus_info.routes[eta.route].name,
			"minutes": eta.time
		})
	else:
		template = "GetNextBuses"
		message = ""
		count = 0
		for eta_info in etas:
			eta = eta_info[0]
			message += "a "+bus_info.routes[eta.route].name+" bus at "+bus_info.stops[eta_info[1]].name+" in "+str(eta.time)+" "+("minute" if eta.time == 1 else "minutes")
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
