from database import *
from flask import Blueprint, request, jsonify

nicknames_endpoint = Blueprint('nicknames_endpoint', __name__)

@nicknames_endpoint.route('/api/v1/nicknames/<ID>', methods=["GET", "PUT", "DELETE"])
def nicknames(ID):
	req_json = request.get_json()

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

@nicknames_endpoint.route('/api/v1/change_nicknames/<ID>', methods=["PUT"])
def change_nicknames(ID):
	req_json = request.get_json()

	try:
		record = Record(ID)
		record.change_nickname(req_json["old_nickname"], req_json["new_nickname"])
	except DatabaseFailure as e:
		return
	return jsonify({"nicknames": record.nicknames, "ID": ID})
