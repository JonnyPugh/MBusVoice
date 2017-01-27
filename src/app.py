from bus_info import BusInfo
from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def launch():
	return statement("Hello, welcome to M-Bus Voice.")

@ask.intent("GetNextBusforStop")
def hello(StopID):
	# Incomplete list of routes
	routes = {100: "Pierpont", 597: "Northwood", 594: "Commuter South", 596: "Commuter North", 633: "Bursley-Baits"}
	
	bus_info = BusInfo(routes.keys())
	estimated_times = bus_info.get_eta(StopID)["etas"][StopID]["etas"][0]
	options = {
		"stopid": StopID,
		"minutes": estimated_times["avg"],
		"busline": routes[estimated_times["route"]]
	}
	text = render_template('GetNextBusforStop', **options)
	return statement(text).simple_card('GetNextBusforStop', text)

if __name__ == "__main__":
	app.run(debug=True)
