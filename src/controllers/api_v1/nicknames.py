from database import *
from flask import Blueprint, request, jsonify

nicknames_endpoint = Blueprint('nicknames_endpoint', __name__)

@nicknames_endpoint.route('/api/v1/nicknames', methods=["GET", "PUT", "DELETE"])
def nicknames():
	req_json = request.get_json()

	ID = req_json["ID"]
	nickname = req_json["nickname"]
	group_type = req_json["type"]
	try:
		record = Record(ID)
		if method == "PUT":
			if group_type != "":
				record.put_nickname(req_json["nickname"], req_json["stops"], group_type == "home")
			else:
				record.put_nickname(req_json["nickname"], req_json["stops"])
		if method == "DELETE":
			record.delete_nickname(req_json["nickname"])
	except DatabaseFailure as e:
		return
	return jsonify({"nicknames": record.nicknames, "ID": ID})

@nicknames_endpoint.route('/api/v1/change_nicknames', methods=["PUT"])
def change_nicknames():
	req_json = request.get_json()

	ID = req_json["ID"]
	try:
		record = Record(ID)
		record.change_nickname(req_json["old_nickname"], req_json["new_nickname"])
	except DatabaseFailure as e:
		return
	return jsonify({"nicknames": record.nicknames, "ID": ID})
