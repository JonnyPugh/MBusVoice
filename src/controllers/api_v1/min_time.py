from database import *
from flask import Blueprint, request, jsonify

min_time_endpoint = Blueprint('min_time_endpoint', __name__)

@min_time_endpoint.route('/api/v1/min_time', methods=["GET", "PUT"])
def min_time():
	req_json = request.get_json()

	ID = req_json["ID"]
	try:
		record = Record(ID)
		if method == "PUT":
			record.min_time = req_json["min_time"]
	except DatabaseFailure as e:
		# Waiting for updated database exceptions
		return 
	return jsonify({"min_time": record.min_time, "ID": ID})
