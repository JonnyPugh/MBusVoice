from extensions import *
from flask import *

get_favorites = Blueprint('get_favorites', __name__, template_folder='templates')

@get_favorites.route('/api/v1/getfavorites', methods=["GET"])
def get_favorite_list():

	try:
		record =  db.get_item(session['alexaID'])
	except database.DatabaseFailure as e:
		jsonify({"errors": [{"message": "Failed to retrieve user info."}]}), 502

	user_stops = get_list_with_stop_type(record['origins'], "Home")
	user_stops.extend(get_list_with_stop_type(record['destinations'], "Destination"))

	def_dest = ""
	if record['default_destination'] != -1:
		def_dest = bus_info.stops[record['default_destination']].name

	return jsonify({'primary': def_dest, 'user_stops': user_stops})

def get_list_with_stop_type(stops, stop_type):
	return [{'alias': alias, 'stop_name': bus_info.stops[stopid].name, 'favorite_type': stop_type} for alias, stopid in stops.iteritems()] 
