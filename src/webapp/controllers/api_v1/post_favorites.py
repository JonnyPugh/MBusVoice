from extensions import *
from quarantine import *
from flask import *

post_favorites = Blueprint('post_favorites', __name__, template_folder='templates')

ORIGIN = "newHome"
DESTINATION = "newDestination"

@post_favorites.route('/api/v1/createfavorite', methods=["POST"])
def create_favorite(): 
	req_json =  request.get_json()

	try:
		verify_proper_request(req_json)
		stop_name = req_json['stop_name']
		req_json['stop_name'] = req_json['stop_name'].lower()

		# Check stopname is in the api -- need access to api object
			# on error, return error
		if not req_json['stop_name'] in bus_info.stops_by_name:
			raise UnprocessableEntity("Given stop_name is not a valid stopname")

		# If the stop alias is not defined, default it to the stop name
		if not req_json['stop_alias']:
			req_json['stop_alias'] = stop_name

		# check if alias (if it exists) is distinct from system aliases/api stops -- need db access
			# on error, return error

		# verify new alias is not too similar to any other user aliases -- need db access
			# if so, throw parameter_error

		user_record = db.get_item(req_json['alexa_id'])

		verify_non_duplicate(req_json, user_record)

	except RequestError as e:
		return e.json, e.code


	# Update the offline version of the user record
	favorite_type = 'origins'
	if req_json['command_type'] == DESTINATION:
		favorite_type = 'destinations'
	user_record[favorite_type][req_json['stop_alias']] = bus_info.stops_by_name[req_json['stop_name']]

	# Insert the update favorite dictionary into the database
	db.update_item_field(req_json['alexa_id'], favorite_type, user_record[favorite_type])

	if 'primary' in req_json and req_json['primary'] == True:
		db.update_item_field(req_json['alexa_id'], 'default_destination', bus_info.stops_by_name[req_json['stop_name']])

	# Return a subset of the response on success
	response_json(req_json, ['primary', 'stop_name'])
	return jsonify(req_json)


def verify_proper_request(req_json):

	parameter_error = verify_json_parameters(['stop_name', 'command_type', 'alexa_id', 'stop_alias'], req_json)

	command_type = req_json['command_type']

	if command_type == DESTINATION and not 'primary' in req_json:
		raise BadRequest("No primary status specified")
	elif command_type == ORIGIN and 'primary' in req_json:
		raise BadRequest("No primary status can be specified for home stops")
	elif command_type != DESTINATION and command_type != ORIGIN:
		raise BadRequest("Invalid command type")

def verify_non_duplicate(req_json, user_record):
	favorite_type = 'origins'
	if req_json['command_type'] == DESTINATION:
		favorite_type = 'destinations'

	if bus_info.stops_by_name[req_json['stop_name']] in user_record[favorite_type].values():
		raise UnprocessableEntity("Insertion of this stop would cause duplication")

def response_json(req_json, remove):
	for key in remove:
		if key in req_json:
			del req_json[key]
