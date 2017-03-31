from database import *
from flask import Blueprint, request, jsonify

order_endpoint = Blueprint('order_endpoint', __name__)

@order_endpoint.route('/api/v1/order/<ID>', methods=["GET"])
def order(ID):
	try:
		record = Record(ID)
	except DatabaseFailure as e:
		return jsonify({"error": "temp error message"})
	return jsonify({"order": record.order, "ID": ID})

