from bus_info import BusInfo
from flask import Blueprint, jsonify

stops_blueprint = Blueprint("stops_blueprint", __name__)

@stops_blueprint.route("/api/v1/stops", methods=["GET"])
def system_stops():
	# Get a mapping of stopIDs to stop names for non-temporary stops
	return jsonify({stopID: stop.name for stopID, stop in BusInfo().stops.items() if stop.name.split()[0] != "(TEMP)"})
