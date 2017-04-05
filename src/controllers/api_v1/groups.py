from database import Record
from request_error import RequestError
from verify_json import *
from flask import Blueprint, request, jsonify

groups_blueprint = Blueprint("groups_blueprint", __name__)

@groups_blueprint.route("/api/v1/<ID>/groups", methods=["GET"])
def get_groups(ID):
	# Get the user's groups
	try:
		return jsonify({"groups": Record(ID).groups})
	except RequestError as e:
		return jsonify(e.json), e.code

@groups_blueprint.route("/api/v1/<ID>/groups/<nickname>", methods=["PUT", "DELETE"])
def groups(ID, nickname):
	# If the request is a PUT request, write the specified
	# stops to the specified group
	# If the request is a DELETE request, delete the specified group
	try:
		record = Record(ID)
		if request.method == "PUT":
			req_json = request.get_json()
			verify(req_json, "stops", list)
			verify(req_json, "type", basestring, ["home", "destination", "other"])
			t = req_json["type"]
			record.put_group(nickname, req_json["stops"], None if t == "other" else t == "home")
			return jsonify({nickname: record.groups[nickname]})
		record.delete_group(nickname)
		return jsonify({"nickname": nickname})
	except RequestError as e:
		return jsonify(e.json), e.code
