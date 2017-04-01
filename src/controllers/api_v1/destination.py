from database import *
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
			if "swap" in req_json:
				record.swap_destination(req_json["swap"])
		return jsonify({"destination": record.destination})
	except DatabaseError as e:
		return jsonify(e.json), e.code		
