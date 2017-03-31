from database import *
from flask import Blueprint, request, jsonify

order_endpoint = Blueprint('order_endpoint', __name__)

@order_endpoint.route('/api/v1/order/<ID>', methods=["GET"])
def order(ID):
	req_json = request.get_json()

	try:
		record = Record(ID)
	except DatabaseFailure as e:
		return
	return jsonify({"order": record.order, "ID": ID})

