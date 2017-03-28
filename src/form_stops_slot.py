from quarantine import BusInfo, data

# Form the slot for all bus stops and aliases
# of those bus stops using API stop names
# and system level stop aliases
info = BusInfo()
with open("stops_slot.txt", "w") as stops_slot_file:
	# Write all API stop names to the slot file
	seen_stops = {}
	for stopid, stop in info.stops.items():
		stop_name = stop.name.lower()
		if stop_name.split()[0] != "(temp)" and stop_name not in seen_stops:
			stops_slot_file.write(stop_name+"\n")
			seen_stops[stop_name] = True

	# Write all system level aliases to the slot file
	for alias in data.stop_aliases.keys():
		stops_slot_file.write(alias+"\n")
