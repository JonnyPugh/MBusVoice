from flask import *

get_favorites = Blueprint('get_favorites', __name__, template_folder='templates')

@get_favorites.route('/api/v1/getfavorites', methods=["GET"])
def get_favorite_list():
	user_stops = get_user_origins(session['alexaID'])
	user_stops.extend(get_user_dests(session['alexaID']))
	primary = get_user_primary(session['alexaID'])
	return jsonify({'primary': primary, 'user_stops': user_stops})

def get_user_origins(alexaID):
	src = {"pierpoint1": 100, "pierpont2": 101}

	return [{'alias': alias, 'stop_name' :stopid, 'favorite_type': "Home"} for alias, stopid in src.iteritems()] 

def get_user_dests(alexaID):
	src = {"class": 137, "work": 138}

	return [{'alias': alias, 'stop_name' :stopid, 'favorite_type': "Destination"} for alias, stopid in src.iteritems()]

def get_user_primary(alexaID):
	return "work"