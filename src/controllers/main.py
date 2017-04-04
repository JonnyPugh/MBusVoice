from database import Record
from request_error import RequestError
from flask import *

main = Blueprint("main", __name__, template_folder="templates")

@main.route("/")
def index():
	# Add the ID to the session if specified as an argument
	# If there's an ID in the session, render the main page
	# If there's no ID in the session and no ID is specified
	# as an argument, return an unauthorized error
	ID = request.args.get("ID")
	if ID:
		# Verify that the specified ID is in the database
		try:
			record = Record(ID)
		except RequestError:
			abort(401)
		session["ID"] = ID
		return redirect(url_for("main.index"))
	elif not "ID" in session:
		abort(401)
	return render_template("index.html", ID=session["ID"])
