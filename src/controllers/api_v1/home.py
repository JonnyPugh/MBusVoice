from extensions import *
from flask import Blueprint, request, jsonify

home_endpoint = Blueprint('home_endpoint', __name__)

@home_endpoint.route('/api/v1/home', methods=["GET", "PUT"])
def home():
	req_json = request.get_json()

	ID = req_json["ID"]
	try:
		record = Record(ID)
		if method == "PUT":
			record.change_nickname(record.home, req_json["home"]) 
	except DatabaseFailure as e:
		return
	return jsonify({"home": record.home, "ID": ID})
