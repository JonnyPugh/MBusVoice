from database import *
from flask import Blueprint, request, jsonify

nicknames_endpoint = Blueprint('nicknames_endpoint', __name__)

@nicknames_endpoint.route('/api/v1/nicknames/<ID>', methods=["GET", "PUT", "DELETE"])
def nicknames(ID):
	try:
		record = Record(ID)
		req_json = request.get_json()
		nickname = req_json["nickname"]

		if request.method == "PUT":
			if req_json["type"] != "":
				record.put_nickname(nickname, req_json["stops"], req_json["type"] == "home")
			else:
				record.put_nickname(nickname, req_json["stops"])
		if method == "DELETE":
			record.delete_nickname(nickname)
	except DatabaseFailure as e:
		return jsonify({"error": "temp error message"})
	return jsonify({"nicknames": record.nicknames, "ID": ID})

@nicknames_endpoint.route('/api/v1/change_nicknames/<ID>', methods=["PUT"])
def change_nicknames(ID):
	req_json = request.get_json()

	try:
		record = Record(ID)
		record.change_nickname(req_json["old_nickname"], req_json["new_nickname"])
	except DatabaseFailure as e:
		return jsonify({"error": "temp error message"})
	return jsonify({"nicknames": record.nicknames, "ID": ID})
