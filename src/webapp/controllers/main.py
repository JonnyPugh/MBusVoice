from flask import *
from stops import stops

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():
	# Add the alexaID to the session if present, if not give error
	alexaID = request.args.get('alexaID')
	if alexaID:
		if alexaID:
			session['alexaID'] = alexaID
		return redirect(url_for('main.index'))
	if not alexaID and not 'alexaID' in session:
		abort(403)
	user_stops = get_user_origins(session['alexaID'])
	user_stops.extend(get_user_dests(session['alexaID']))
	primary = get_user_primary(session['alexaID'])
	options = {
		'alexaID': session['alexaID'],
		'stop_names': stops,
		'user_stops': user_stops,
		'primary': primary
	}
	return render_template("index.html", **options)

def get_user_origins(alexaID):
	src = {"pierpoint1": 100, "pierpont2": 101}

	return [(alias, stopid, "Home") for alias, stopid in src.iteritems()] 

def get_user_dests(alexaID):
	src = {"class": 137, "work": 138}

	return [(alias, stopid, "Destination") for alias, stopid in src.iteritems()]

def get_user_primary(alexaID):
	return "class"