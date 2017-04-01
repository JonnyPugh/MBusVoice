from database import *
from flask import Blueprint, request, jsonify

nicknames_blueprint = Blueprint("nicknames_blueprint", __name__)

@nicknames_blueprint.route("/api/v1/<ID>/nicknames", methods=["GET"])
def get_nicknames(ID):
	# Get the user's groups
	try:
		return jsonify({"nicknames": Record(ID).nicknames})
	except DatabaseError as e:
		return jsonify(e.json), e.code

@nicknames_blueprint.route("/api/v1/<ID>/<nickname>", methods=["PUT", "DELETE"])
def nicknames(ID, nickname):
	# If the request is a PUT request, write the specified
	# stops to the specified nickname and change the nickname
	# if a new_nickname is specified
	# If the request is a DELETE request, delete the specified group
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			if "new_nickname" in req_json:
				record.change_nickname(nickname, req_json["new_nickname"])
				nickname = req_json["new_nickname"]
			if "stops" in req_json:
				home = None
				if "type" in req_json and req_json["type"] in ["home", "destination"]:
					home = req_json["type"] == "home"
				record.put_nickname(nickname, req_json["stops"], home)
			if nickname in record.nicknames:
				return jsonify({nickname: record.nicknames[nickname]})
		else:
			record.delete_nickname(nickname)
		return jsonify({})
	except DatabaseError as e:
		return jsonify(e.json), e.code
