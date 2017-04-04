from database import Record
from request_error import RequestError
from verify_json import verify
from flask import Blueprint, request, jsonify

time_blueprint = Blueprint("time_blueprint", __name__)

@time_blueprint.route("/api/v1/<ID>/time", methods=["GET", "PUT"])
def time(ID):
	# If the request is a PUT request, change the 
	# user's time to the specified time
	# Get the user's time
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			verify(req_json, "time", int)
			record.time = req_json["time"]
		return jsonify({"time": record.time})
	except RequestError as e:
		return jsonify(e.json), e.code
