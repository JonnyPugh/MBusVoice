#!/usr/bin/env python

from quarantine import BusInfo
from time import ctime, sleep
import os

# Change working directory to the directory of this script the files
# are created in this directory no matter where the script is run
os.chdir(os.path.dirname(os.path.abspath(__file__)))

routes = {}
while True:
	with open("interaction_model/routes.txt", "w") as routes_file:
		with open("interaction_model/routes_slot.txt", "w") as routes_slot:
			routes_file.write("All Discovered Routes as of "+ctime()+":\n")
			routes.update(BusInfo().routes)
			for route_id, route in routes.items():
				routes_file.write("_____________________________________________________\n")
				routes_file.write("Route name: "+route.name+"\n")
				routes_file.write("ID: "+str(route_id)+"\n")
				routes_file.write("Description: "+route.description+"\n")
				routes_file.write("Start time: "+route.start_time+"\n")
				routes_file.write("End time: "+route.end_time+"\n")
				routes_file.write("Stops: "+str(route.stops)+"\n")
				routes_slot.write(route.name.lower()+"\n")
	sleep(300)
