from extensions import *
from flask import *

post_favorites = Blueprint('post_favorites', __name__, template_folder='templates')

ORIGIN = "newHome"
DESTINATION = "newDestination"

@post_favorites.route('/api/v1/createfavorite', methods=["POST"])
def create_favorite(): 
	req_json =  request.get_json()

	malformed_request_error = verify_proper_request(req_json)

	if malformed_request_error is not None:
		return malformed_request_error

	# Check stopname is in the api -- need access to api object
		# on error, return error

	# check if alias (if it exists) is distinct from system aliases/api stops -- need db access
		# on error, return error

	# verify that user exists (can skip duplication checking) -- need db access
		# If not, create and skip duplication prevention logic

	# verify new alias is not too similar to any other user aliases -- need db access
		# if so, throw error

	duplication_error = duplicate_entries(req_json['command_type'], req_json['stop_name'], req_json['alexa_id'])

	if duplication_error is not None:
		return duplication_error

	# check that the stop is not already a home or destination
	# insert into db
	insert_db(req_json)

	# if destination and no primary destination has been set, make primary, or if indicated should be primary
	response_json(req_json, ['primary', 'stop_name'])
	return jsonify(req_json)


def verify_proper_request(req_json):

	parameter_error = verify_json_parameters(['stop_name', 'command_type', 'alexa_id', 'stop_alias'], req_json)

	if parameter_error is not None:
		return parameter_error

	command_type = req_json['command_type']

	if command_type == DESTINATION and not 'primary' in req_json:
		return jsonify({"errors": [{"message": "No primary status specified"}]}), 400
	elif command_type == ORIGIN and 'primary' in req_json:
		return jsonify({"errors": [{"message": "No primary status can be specified for home stops"}]}), 400
	elif command_type != DESTINATION and command_type != ORIGIN:
		return jsonify({"errors": [{"message": "Invalid command type"}]}), 400

	return None

def duplicate_entries(command_type, stop_name, alexa_id):
	return None

	
def insert_db(req_json):
	target_field = "origin"
	if req_json['command_type'] == DESTINATION:
		target_field = "destination"

	return

def response_json(req_json, remove):
	for key in remove:
		if key in req_json:
			del req_json[key]
