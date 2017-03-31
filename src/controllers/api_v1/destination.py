from database import *
from flask import Blueprint, request, jsonify

destination_endpoint = Blueprint('destination_endpoint', __name__)

@destination_endpoint.route('/api/v1/destination/<ID>', methods=["GET"])
def destination(ID):
	try:
		record = Record(ID)
	except DatabaseFailure as e:
		return jsonify({"error": "temp error message"})
	return jsonify({"destination": record.destination, "ID": ID})

@destination_endpoint.route('/api/v1/swap_destination/<ID>', methods=["PUT"])
def swap_destination(ID):
	req_json = request.get_json()
	try:
		record = Record(ID)
		record.swap_destination(req_json["nickname"])
	except DatabaseFailure as e:
		return jsonify({"error": "temp error message"})
	return jsonify({"destination": record.destination, "ID": ID})