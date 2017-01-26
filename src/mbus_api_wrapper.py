import requests

# API routes found https://github.com/ishbaid/BlueBus

# Incomplete list of routes
routes = {597: "Northwood", 594: "Commuter South", 596: "Commuter North", 633: "Bursley-Baits"}

# Need to write logic to account for stops that have no buses incoming or do not exist
# Will have to breakout of regular flow and return an error string to the user
def get_buses_for_stop(stopNum):
	resp = requests.get('http://mbus.doublemap.com/map/v2/eta?stop=' + str(stopNum))

	if 'error' in resp.json():
		return []

	return resp.json()['etas'][str(stopNum)]['etas']
