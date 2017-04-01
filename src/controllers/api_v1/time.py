from database import *
from flask import Blueprint, request, jsonify

time_blueprint = Blueprint("time_blueprint", __name__)

@time_blueprint.route("/api/v1/<ID>/time", methods=["GET", "PUT"])
def min_time(ID):
	# If the request is a PUT request, change the 
	# user's time to the specified time
	# Get the user's time
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			if "time" in req_json:
				record.min_time = req_json["time"]
		return jsonify({"time": record.min_time})
	except DatabaseError as e:
		return jsonify(e.json), e.code
