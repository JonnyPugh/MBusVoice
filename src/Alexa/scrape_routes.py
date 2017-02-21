#!/usr/bin/env python

from bus_info import BusInfo
from time import ctime

with open("interaction_model/routes.txt", "w") as routes_file:
	routes_file.write("All Discovered Routes as of "+ctime()+":\n")
	for route_id, route in BusInfo().routes.items():
		routes_file.write("_____________________________________________________\n")
		routes_file.write("Route name: "+route.name+"\n")
		routes_file.write("ID: "+str(route_id)+"\n")
		routes_file.write("Description: "+route.description+"\n")
		routes_file.write("Start time: "+route.start_time+"\n")
		routes_file.write("End time: "+route.end_time+"\n")
		routes_file.write("Stops: "+str(route.stops)+"\n")
