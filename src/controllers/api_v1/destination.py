from database import Record
from request_error import RequestError
from verify_json import verify
from flask import Blueprint, request, jsonify

destination_blueprint = Blueprint("destination_blueprint", __name__)

@destination_blueprint.route("/api/v1/<ID>/destination", methods=["GET"])
def destination(ID):
	# Get the user's destination nickname
	try:
		return jsonify({"destination": Record(ID).destination})
	except RequestError as e:
		return jsonify(e.json), e.code		
