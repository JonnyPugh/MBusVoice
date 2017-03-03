from quarantine import *

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