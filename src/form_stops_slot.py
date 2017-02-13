from bus_info import BusInfo

info = BusInfo()
with open("interaction_model/stops_slot.txt", "w") as stops_slot_file:
	seen_stops = {}
	for stopid, stop in info.stops.items():
		if stop.name.split()[0] != "(TEMP)" and stop.name not in seen_stops:
			stops_slot_file.write(stop.name+"\n")
			seen_stops[stop.name] = True
