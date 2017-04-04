from database import Record
from request_error import RequestError
from flask import Blueprint, jsonify

home_blueprint = Blueprint("home_blueprint", __name__)

@home_blueprint.route("/api/v1/<ID>/home", methods=["GET"])
def home(ID):
	# Get the user's home nickname
	try:
		return jsonify({"home": Record(ID).home})
	except RequestError as e:
		return jsonify(e.json), e.code
