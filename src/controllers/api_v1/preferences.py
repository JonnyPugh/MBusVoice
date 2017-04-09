from database import Record
from request_error import RequestError
from flask import Blueprint, request, jsonify

preferences_blueprint = Blueprint("preferences_blueprint", __name__)

@preferences_blueprint.route("/api/v1/<ID>/preferences", methods=["GET", "PUT"])
def preferences(ID):
	# If the request is a PUT, verify the incoming 
	# JSON and write it to the database
	# Get the user's preferences
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			__verify(req_json, "time", int)
			__verify_key(req_json, "home")
			if req_json["home"] != None:
				__verify_type(req_json["home"], basestring)
			__verify_key(req_json, "destination")
			if req_json["destination"] != None:
				__verify_type(req_json["destination"], basestring)
			__verify(req_json, "groups", dict)
			for nickname in req_json["groups"]:
				__verify(req_json["groups"], nickname, list)
			__verify(req_json, "order", list)
			record.time = req_json["time"]
			record.groups = req_json["groups"]
			record.home = req_json["home"]
			record.destination = req_json["destination"]
			record.order = req_json["order"]
		return jsonify({
			"time": record.time,
			"home": record.home,
			"destination": record.destination,
			"groups": record.groups,
			"order": record.order
		})
	except RequestError as e:
		return jsonify(e.json), e.code

# Verify that the key is in the JSON, and its value is of type t
def __verify(json, key, t):
	__verify_key(json, key)
	__verify_type(json[key], t)

# Verify that the key is in the JSON
def __verify_key(json, key):
	if key not in json:
		raise _JSONKeyError(key)

# Verify that the specified value has the specified type
def __verify_type(value, t):
	if not isinstance(value, t):
		raise _JSONTypeError(t.__name__)

# Internal errors used by the verification functions
class _JSONError(RequestError):
	def __init__(self, expected, value):
		super(_JSONError, self).__init__("Expected a " + expected + " of '" + value + "'", 400)

class _JSONKeyError(_JSONError):
	def __init__(self, key):
		super(_JSONKeyError, self).__init__("key", key)

class _JSONTypeError(_JSONError):
	def __init__(self, t):
		super(_JSONTypeError, self).__init__("type", t)

class _JSONValueError(_JSONError):
	def __init__(self, values):
		super(_JSONValueError, self).__init__("value", "/".join(values))
