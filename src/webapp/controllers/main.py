from flask import *

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def main_route():
	alexaID = request.args.get('alexaID')
	return render_template("index.html", alexaID=alexaID)
