from extensions import *
from flask import *
from copy import deepcopy

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

		user_record = db.get_item(req_json['alexa_id'])

		verify_non_duplicate(req_json, user_record)

		# clarifyStopName will throw an exception if the given alias
		# does not conflict with existing aliases

		if req_json['stop_alias'].lower() != stop_name.lower():
			aliases = deepcopy(user_record['origins'])
			aliases.update(user_record['destinations'])
			#shared.clarifyStopName(req_json['stop_alias'], aliases)
			# FLAG: Change this error handling to fit new structure

			# If clarifyStopName did not throw an exception, throw one to indicate
			# the given stop alias is too similar to an existing alias
			#raise UnprocessableEntity("This alias is too similar to another alias")

	except RequestError as e:
		return e.json, e.code
	except InvalidPhrase as e:
		pass

	# Update the offline version of the user record
	favorite_type = 'origins'
	if req_json['command_type'] == DESTINATION:
		favorite_type = 'destinations'
	user_record[favorite_type][req_json['stop_alias']] = bus_info.stops_by_name[req_json['stop_name']]

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
	stop_id = bus_info.stops_by_name[req_json['stop_name']]
	print stop_id
	if stop_id in user_record['origins'].values() or stop_id in user_record['destinations'].values():
		raise UnprocessableEntity("You already an alias for this stop")

def response_json(req_json, remove):
	for key in remove:
		if key in req_json:
			del req_json[key]
