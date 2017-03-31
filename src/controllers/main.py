from database import *
from flask import abort, Blueprint, session, redirect, request

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():
	# Add the alexaID to the session if present, if not give error

	ID = request.args.get('ID')
	if ID:
		#check if the alexaID is in the db, should be added when card is first sent
		#if not in db, do not show them main page
		try:
			record = Record(ID)
		except DatabaseFailure as e:
			abort(403)

		session['ID'] = ID
		return redirect(url_for('main.index'))
	if not ID and not "ID" in session:
		abort(403)

	options = {
		'ID': session['ID'],
	}
	return render_template("index.html", **options)
