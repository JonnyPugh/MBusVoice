from flask import *

favorites = Blueprint('favorites', __name__, template_folder='templates')

@favorites.route('/api/v1/homefavorite')
def homefavorite(): 
	# Skeleton for receiving home form posting
	return 


@favorites.route('/api/v1/destinationfavorite')
def destinationfavorite():
	# Skeleton for receiving destination form posting
	return 
