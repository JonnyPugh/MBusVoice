from flask import jsonify


class RequestError(Exception):
	def __init__(self, message, code):
		self.code = code
		self.json = jsonify({"errors": [{"message": message}]})
		super(Exception, self).__init__(message)

class BadRequest(RequestError):
	def __init__(self, message):
		super(RequestError, self).__init__(message, 400)

class UnprocessableEntity(RequestError):
	def __init__(self, message):
		super(RequestError, self).__init__(message, 422)

def verify_json_parameters(parameters, json):
    for parameter in parameters:
        if parameter not in json:
            raise BadRequest("You did not provide the necessary fields")


#####################################################
#       DUPLICATED CODE FROM ALEXA.INTENTS.PY       #
#####################################################
# Exception class used to indicate invalid stop names
class InvalidStop(Exception):
	def __init__(self, stop_name):
		super(Exception, self).__init__(stop_name+" is not a valid stop name")

# Take the user's spoken stop name and figure out which stop 
# id(s) they are referring to and return it/them as a list.
def clarifyStopName(user_phrase):
	# Use system level aliases and the stops given by the API and 
	# see if the user was referring to one of those stops
	user_phrase = user_phrase.lower()
	if user_phrase in bus_info.stops_by_name:
		return user_phrase, [bus_info.stops_by_name[user_phrase]]
	if user_phrase in stop_aliases:
		return user_phrase, stop_aliases[user_phrase]

	# If the specified stop name is similar to a user level alias,
	# return all stop ids associated with that alias
	user_aliases = {}

	# If the specified stop name is similar to a system level alias or 
	# a stop name, return all stop ids associated with it
	close_matches = get_close_matches(user_phrase, bus_info.stops_by_name.keys())
	if close_matches:
		name = close_matches[0]
		return name, [stops_by_name[name]]
	close_matches = get_close_matches(user_phrase, stop_aliases.keys())
	if close_matches:
		name = close_matches[0]
		return name, stop_aliases[name]

	# Raise an error if the user_phrase couldn't be clarified
	raise InvalidStop(user_phrase)
