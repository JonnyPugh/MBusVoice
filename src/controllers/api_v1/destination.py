from database import Record
from request_error import RequestError
from verify_json import verify
from flask import Blueprint, request, jsonify

destination_blueprint = Blueprint("destination_blueprint", __name__)

@destination_blueprint.route("/api/v1/<ID>/destination", methods=["GET", "PUT"])
def destination(ID):
	# If the request is a PUT request, swap the user's 
	# destination group with the specified group
	# Get the user's destination nickname
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			verify(req_json, "swap", basestring)
			record.swap_destination(req_json["swap"])
		return jsonify({"destination": record.destination})
	except RequestError as e:
		return jsonify(e.json), e.code		
