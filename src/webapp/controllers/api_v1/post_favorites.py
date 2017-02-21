from flask import *

post_favorites = Blueprint('post_favorites', __name__, template_folder='templates')

@post_favorites.route('/api/v1/createfavorite')
def create_favorite(): 
	# if a new home stop
		# ensure there is a stopname and alias

	# if new dest stop
		# ensure stopname and alias

	# Check stopname is in the api
		# on error, return error

	# check if alias (if it exists) is distinct from system aliases/api stops
		# on error, return error

	# check that the stop is not already a home or destination
	# insert into db

	# if destination and no primary destination has been set, make primary, or if indicated should be primary
	return 