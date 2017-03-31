from database import *
from flask import Blueprint, request, jsonify

home_endpoint = Blueprint('home_endpoint', __name__)

@home_endpoint.route('/api/v1/home/<ID>', methods=["GET"])
def home(ID):
	try:
		record = Record(ID)
	except DatabaseFailure as e:
		return jsonify({"error": "Everything exploded"})
	return jsonify({"home": record.home, "ID": ID})
