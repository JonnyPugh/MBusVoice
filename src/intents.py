from bus_info import BusInfo
from database import Database
from data import stop_aliases
from flask import Blueprint, render_template
from flask_ask import Ask, statement, session
from difflib import get_close_matches

blueprint = Blueprint("MBus_blueprint", __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

bus_info = BusInfo()
db = Database()

# Exception class used to indicate invalid stop names
class InvalidPhrase(Exception):
	def __init__(self, stop_name):
		super(Exception, self).__init__(stop_name+" is not a valid stop name")

# Take the user's spoken stop name and figure out which stop 
# id(s) they are referring to and return it/them as a list.
def clarifyStopName(user_phrase, favorite_stops):
	# Use system level aliases and the stops given by the API and 
	# see if the user was referring to one of those stops
	user_phrase = user_phrase.lower()
	if user_phrase in bus_info.stops_by_name:
		return user_phrase, [bus_info.stops_by_name[user_phrase]]
	if user_phrase in stop_aliases:
		return user_phrase, stop_aliases[user_phrase]

	# If the specified stop name is similar to a user level alias,
	# return the stop id associated with that alias
	close_matches = get_close_matches(user_phrase, favorite_stops.keys())
	if close_matches:
		name = close_matches[0]
		return name, [favorite_stops[name]]

	# If the specified stop name is similar to a system level alias or 
	# a stop name, return all stop ids associated with it
	close_matches = get_close_matches(user_phrase, bus_info.stops_by_name.keys())
	if close_matches:
		name = close_matches[0]
		return name, [bus_info.stops_by_name[name]]
	close_matches = get_close_matches(user_phrase, stop_aliases.keys())
	if close_matches:
		name = close_matches[0]
		return name, stop_aliases[name]

	# Raise an error if the user_phrase couldn't be clarified
	raise InvalidPhrase(user_phrase)

# If the current user is not in the database, add them to the database 
# Return the current user's data
def getUserData():
	userID = session.user.userId
	try:
		return db.get_item(userID)
	except database.DatabaseFailure:
		db.put_item(userID, {}, {}, -1)
		return db.get_item(userID)

# Get the message to put in the card that tells users 
# the URL of the deployed web application
def getPreferencesCard():
	return "Set up your preferences at: https://szxtj7qm84.execute-api.us-east-1.amazonaws.com/dev?alexaID="+session.user.userId

# Introduce the skill and demonstrate how to use it
# If the current user is not in the database, add them to the database
@ask.launch
def launch():
	getUserData()
	return statement(render_template("Open")).simple_card("Welcome!", getPreferencesCard())

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
	user_info = getUserData()
	template = "MissingFavorite"

	try:
		# Try to understand which stops the user is talking about
		if StartStop:
			StartStop, start_stops = sclarifyStopName(StartStop, user_info["origins"])
		else:
			start_stops = user_info["origins"].values()
			if not start_stops:
				return statement(render_template(template, stopType="starting", favoriteType="home")).simple_card("No Home Stops Set", getPreferencesCard())
		if EndStop:
			EndStop, end_stops = clarifyStopName(EndStop, user_info["destinations"])
		else:
			stopID = user_info["default_destination"]
			if stopID == -1:
				return statement(render_template(template, stopType="ending", favoriteType="destination")).simple_card("No Destination Stop Set", getPreferencesCard())
			end_stops = [stopID]
			EndStop = {stopid: alias for alias, stopid in user_info["destinations"].items()}[stopID]
	except InvalidPhrase as e:
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
		return statement(text)

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
			"origin": (StartStop if len(start_stops) == 1 else bus_info.stops[stopID].name).replace(" -", ""),
			"route": bus_info.routes[eta.route].name,
			"minutes": eta.time
		})
	else:
		template = "GetNextBuses"
		message = ""
		count = 0
		for eta_info in etas:
			eta = eta_info[0]
			message += "a "+bus_info.routes[eta.route].name+" bus at "+bus_info.stops[eta_info[1]].name.replace(" -", "")+" in "+str(eta.time)+" "+("minute" if eta.time == 1 else "minutes")
			count += 1
			if count == NumBuses or count == len(etas):
				break
			message += ", "
			if count == NumBuses - 1 or count == len(etas) - 1:
				message += "and "
		options.update({
			"busInfo": message
		})
	text = render_template(template, **options)
	return statement(text)

# Get the next bus coming to a specified stop
@ask.intent("GetNextBusAtStop")
def getNextBuses(StopName):
	try:
		StopName, start_stops = clarifyStopName(StopName, getUserData()["origins"])
	except InvalidPhrase as e:
		return statement(e.message)

	# Determine the soonest eta to the specified stop
	eta = None
	for start_stop in start_stops:
		for stop_eta in bus_info.get_eta(start_stop):
			if not eta or stop_eta.time < eta.time:
				eta = stop_eta
				eta_stop = start_stop

	# If there are no etas, return an error message
	if not eta:
		template = "NoBuses"
		text = render_template(template, origin=StopName)
		return statement(text)

	# Form the response and return it to the user
	template = "GetNextBusAtStop"
	text = render_template(template, 
		origin=(StopName if len(start_stops) == 1 else bus_info.stops[eta_stop].name).replace(" -", ""),
		route=bus_info.routes[eta.route].name,
		minutes=eta.time)
	return statement(text)
