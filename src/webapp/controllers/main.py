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
		return "welcome to hell", 404
	options = {
		'alexaID': session['alexaID'],
		'stop_names': stops
	}
	return render_template("index.html", **options)

