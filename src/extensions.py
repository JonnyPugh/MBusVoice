from bus_info import BusInfo
from flask import jsonify

bus_info = BusInfo()

class RequestError(Exception):
	def __init__(self, message, code):
		self.code = code
		self.json = jsonify({"errors": [{"message": message}]})
		super(RequestError, self).__init__(message)

class BadRequest(RequestError):
	def __init__(self, message):
		super(BadRequest, self).__init__(message, 400)

class UnprocessableEntity(RequestError):
	def __init__(self, message):
		super(UnprocessableEntity, self).__init__(message, 422)

def verify_json_parameters(parameters, json):
    for parameter in parameters:
        if parameter not in json:
            raise BadRequest("You did not provide the necessary fields")
