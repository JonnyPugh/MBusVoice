from quarantine import *
from flask import *
from stops import stops

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():
	# Add the alexaID to the session if present, if not give error

	alexaID = request.args.get('alexaID')
	if alexaID:
		#check if the alexaID is in the db, should be added when card is first sent
		#if not in db, do not show them main page
		try:
			record = db.get_item(alexaID)
		except KeyError as e:
			abort(403)

		session['alexaID'] = alexaID
		return redirect(url_for('main.index'))
	if not alexaID and not 'alexaID' in session:
		abort(403)

	options = {
		'alexaID': session['alexaID'],
		'stop_names': stops,
	}
	return render_template("index.html", **options)