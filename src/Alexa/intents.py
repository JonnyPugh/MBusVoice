from quarantine import *
from flask import Blueprint, render_template
from flask_ask import Ask, statement, session
from difflib import get_close_matches
from boto3 import resource

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
	# If parameters are None, get user values from the database
	if not StartStop or not EndStop:
	    item = resource("dynamodb", region_name="us-east-1").Table("UserFavorites").get_item(
	        Key={
				"AlexaID": str(session.user.userId)
			}
	    )["Item"]
	    template = "MissingFavorite"

	try:
		# Try to understand which stop the user is talking about
		if StartStop:
			StartStop, start_stops = clarify_stop_name.clarifyStopName(StartStop)
		else:
			start_stops = item["origins"].values()
			if not start_stops:
				text = render_template(template, stopType="starting", favoriteType="home")
				return statement(text).simple_card(template, text)
		if EndStop:
			EndStop, end_stops = clarify_stop_name.clarifyStopName(EndStop)
		else:
			stopID = item["primary"]
			end_stops = [stopID]
			if not end_stops:
				text = render_template(template, stopType='ending', favoriteType='destination')
				return statement(text).simple_card(template, text)
			EndStop = {stopid: alias for alias, stopid in item['destinations'].items()}[stopID]
	except clarify_stop_name.InvalidUserAlias as e:
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
	etas = sorted(etas, key=lambda eta_info: eta_info[0].time)

	# If there are no valid etas, return an error message
	if not etas:
		text = render_template("NoEtas", 
			route=RouteName if RouteName else "", 
			origin=StartStop if StartStop else "your home stops", 
			destination=EndStop)
		return statement(text).simple_card(template, text)

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
			StartStop = {stopid: alias for alias, stopid in item["origins"].items()}[stopID]	
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
