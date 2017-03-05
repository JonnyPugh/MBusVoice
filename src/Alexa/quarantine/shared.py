from bus_info import BusInfo
from database import Database
from data import stop_aliases
from difflib import get_close_matches
from flask import jsonify

bus_info = BusInfo()
db = Database()

class RequestError(Exception):
	def __init__(self, message, code):
		self.code = code
		self.json = jsonify({"errors": [{"message": message}]})
		super(Exception, self).__init__(message)

# Exception class used to indicate invalid stop names
class InvalidUserAlias(Exception):
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
	raise InvalidUserAlias(user_phrase)
	