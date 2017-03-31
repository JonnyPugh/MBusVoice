from database import *
from flask import Blueprint, request, jsonify

min_time_endpoint = Blueprint('min_time_endpoint', __name__)

@min_time_endpoint.route('/api/v1/min_time/<ID>', methods=["GET", "PUT"])
def min_time(ID):
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			record.min_time = req_json["min_time"]
	except DatabaseFailure as e:
		# Waiting for updated database exceptions
		return jsonify({"error": "temp error message"})
	return jsonify({"min_time": record.min_time, "ID": ID})
