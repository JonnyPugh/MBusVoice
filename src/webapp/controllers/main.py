from flask import *
from stops import stops

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():
	alexaID = request.args.get('alexaID')
	print stops
	options = {
		'alexaID': alexaID,
		'stop_names': stops
	}
	return render_template("index.html", **options)
