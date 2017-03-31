from extensions import *
from flask import Blueprint, request, jsonify

order_endpoint = Blueprint('order_endpoint', __name__)

@order_endpoint.route('/api/v1/order', methods=["GET"])
def order():
	req_json = request.get_json()

	ID = req_json["ID"]
	try:
		record = Record(ID)
	except DatabaseFailure as e:
		return
	return jsonify({"order": record.order, "ID": ID})

