from database import *
from flask import Blueprint, request, jsonify

destination_endpoint = Blueprint('destination_endpoint', __name__)

@destination_endpoint.route('/api/v1/destination', methods=["GET", "PUT"])
def destination():
	req_json = request.get_json()

	ID = req_json["ID"]
	try:
		record = Record(ID)
		if method == "PUT":
			record.change_nickname(record.destination, req_json["destination"])
	except DatabaseFailure as e:
		return
	return jsonify({"destination": record.destination, "ID": ID})

@destination_endpoint.route('/api/v1/swap_destination', methods=["PUT"])
def swap_destination():
	req_json = request.get_json()

	ID = req_json["ID"]
	try:
		record = Record(ID)
		record.swap_destination(req_json["nickname"])
	except DatabaseFailure as e:
		return
	return jsonify({"destination": record.destination, "ID": ID})