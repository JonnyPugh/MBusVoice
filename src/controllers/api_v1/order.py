from database import Record
from request_error import RequestError
from flask import Blueprint, jsonify

order_blueprint = Blueprint("order_blueprint", __name__)

@order_blueprint.route("/api/v1/<ID>/order", methods=["GET"])
def order(ID):
	# Get the user's order
	try:
		return jsonify({"order": Record(ID).order})
	except RequestError as e:
		return jsonify(e.json), e.code
