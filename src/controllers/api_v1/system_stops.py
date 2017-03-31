from bus_info import BusInfo
from flask import Blueprint, jsonify

system_stops_endpoint = Blueprint('system_stops_endpoint', __name__)

@system_stops_endpoint.route('/api/v1/system_stops', methods=["GET"])
def system_stops():
	bus_info = BusInfo()
	return jsonify(bus_info.stop_by_name)