from bus_info import BusInfo
from data import stop_aliases
from flask import Blueprint, render_template
from flask_ask import Ask, statement, session
from difflib import get_close_matches

import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

blueprint = Blueprint("MBus_blueprint", __name__, url_prefix="/")
ask = Ask(blueprint=blueprint)

bus_info = BusInfo()

# Introduce the skill and demonstrate how to use it
@ask.launch
def launch():
	return statement("Hello, welcome to M-Bus Voice.")

# Exception class used to indicate invalid stop names
class InvalidStop(Exception):
	def __init__(self, message):
		super(Exception, self).__init__(message)

# Take the user's spoken stop name and figure out which stop 
# id(s) they are referring to and return it/them as a list.
def clarifyStopName(user_phrase):
	# Use system level aliases and the stops given by the API and 
	# see if the user was referring to one of those stops
	stops_by_name = bus_info.stops_by_name
	stops_by_name.update(stop_aliases)
	user_phrase = user_phrase.lower()
	if user_phrase in stops_by_name:
		return user_phrase, stops_by_name[user_phrase]

	# If the specified stop name is similar to a user level alias,
	# return all stop ids associated with that alias
	user_aliases = {}

	# If the specified stop name is similar to a system level alias,
	# return all stop ids associated with that alias
	close_matches = get_close_matches(user_phrase, stops_by_name.keys())
	if close_matches:
		name = close_matches[0]
		return name, stops_by_name[name]

	# Raise an error if the user_phrase couldn't be clarified
	raise InvalidStop(user_phrase+" is not a valid stop name")

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
		dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
		table = dynamodb.Table('UserFavorites')
		try:
		    response = table.get_item(
		        Key={
					'AlexaID': str(session.user.userId)
				}
		    )
		except ClientError as e:
		    print(e.response['Error']['Message'])
		else:
		    item = response['Item']
		    print (item)	

	try:
		# Try to understand which stop the user is talking about
		if StartStop:
			StartStop, start_stops = clarifyStopName(StartStop)
		else:
			start_stops = item['origins'].values()

			if not start_stops:
				template = 'MissingFavorite'
				text = render_template(template, stopType='starting', favoriteType='home')
				return statement(text).simple_card(template, text)

		if EndStop:
			EndStop, end_stops = clarifyStopName(EndStop)
		else:
			stopID = item['primary']
			end_stops = [stopID]

			if not end_stops:
				template = 'MissingFavorite'
				text = render_template(template, stopType='ending', favoriteType='destination')
				return statement(text).simple_card(template, text)

			EndStop = {stopid: alias for alias, stopid in item['destinations'].items()}[stopID]

	except InvalidStop as e:
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
		return statement("No "+(RouteName if RouteName else "")+" buses are currently going from "+StartStop+" to "+EndStop)

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
			StartStop = {stopid: alias for alias, stopid in item['origins'].items()}[stopID]
			

		options.update({
			"origin": StartStop if len(start_stops) == 1 and StartStop else bus_info.stops[stopID].name,
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
