from extensions import *
from flask import *

edit_favorites = Blueprint('edit_favorites', __name__, template_folder='templates')

@edit_favorites.route('/api/v1/changeprimary', methods=["POST"])
def change_primary():
	req_json = request.get_json()
	
	try:
		verify_json_parameters(['alexa_id', 'stop_alias'], req_json)

		# ensure user exists -- need db access

		# ensure the user already has this alias set in the database -- need db access

	except RequestError as e:
		return e.json, e.code
	# Update -- need db access

	return jsonify(req_json), 200

@edit_favorites.route('/api/v1/deletefavorite', methods=["POST"])
def delete_favorite():
	req_json = request.get_json()

	try:
		malformed_request_error = verify_json_parameters(['alexa_id', 'stop_alias'], req_json)

		# check that the user exists -- need db access

		# check that this data exists in user home or destinations
			# throw error if not
	except RequestError as e:
		return e.json, e.code

	# if deleting primary
		# clear primary field

	# delete item from field

	return jsonify(alexa_id=req_json['alexa_id']), 200



