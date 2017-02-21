from flask import *

edit_favorites = Blueprint('edit_favorites', __name__, template_folder='templates')

@edit_favorites.route('/api/v1/deletefavorite')
def delete_favorite():
	# Ensure AlexaID and stop alias were given 
	# check that this data exists in user home or destinations
		# throw error if not
	# if deleting primary
		# clear primary field
	# delete item from field
	return 


@edit_favorites.route('/api/v1/changeprimary')
def change_primary():
	# Ensure alexaID and stop alias were given 
		# ensure the user already has this alias set in db
			# throw error if not
	# Update 
	# Skeleton for receiving destination form posting
	return 


