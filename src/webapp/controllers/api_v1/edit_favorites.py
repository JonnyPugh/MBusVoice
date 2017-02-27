from extensions import *
from quarantine import *
from flask import *

edit_favorites = Blueprint('edit_favorites', __name__, template_folder='templates')

@edit_favorites.route('/api/v1/changeprimary', methods=["POST"])
def change_primary():
	req_json = request.get_json()
	
	try:
		verify_json_parameters(['alexa_id', 'stop_alias'], req_json)

		user_record = db.get_item(req_json['alexa_id'])

		if not req_json['stop_alias'] in user_record['destinations']:
			raise BadRequest("Cannot change non existent destination to be primary")

	except RequestError as e:
		return e.json, e.code
	
	db.update_item_field(req_json['alexa_id'], 'default_destination', user_record['destinations'][req_json['stop_alias']])

	return jsonify(req_json), 200

@edit_favorites.route('/api/v1/deletefavorite', methods=["POST"])
def delete_favorite():
	req_json = request.get_json()

	try:
		malformed_request_error = verify_json_parameters(['alexa_id', 'stop_alias'], req_json)

		user_record = db.get_item(req_json['alexa_id'])

		# check that this data exists in user home or destinations
			# throw error if not
		favorite_type = determine_favorite_type(req_json['stop_alias'], user_record)

	except RequestError as e:
		return e.json, e.code

	print user_record
	if user_record[favorite_type][req_json['stop_alias']] == user_record['default_destination']:
		# There appears to be a bug, becuse this causes a DatabaseError to be thrown
		db.update_item_field(req_json['alexa_id'], 'default_destination', "")

	# Remove the alias from the user_record
	user_record[favorite_type].pop(req_json['stop_alias'])
	print user_record

	db.update_item_field(req_json['alexa_id'], favorite_type, user_record[favorite_type])

	return jsonify(alexa_id=req_json['alexa_id']), 200

def determine_favorite_type(stop_alias, user_record):
	if stop_alias in user_record['origins']:
		return 'origins'
	elif stop_alias in user_record['destinations']:
		return 'destinations'
	
	raise BadRequest("Cannot delete non existent stop")



