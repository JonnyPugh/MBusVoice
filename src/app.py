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
	bus_info = BusInfo([100, 597, 594, 596, 633])
	eta = bus_info.get_eta(StopID).values()[0]
	options = {
		"stopid": StopID,
		"minutes": eta.time,
		"busline": bus_info.routes[eta.route].name
	}
	text = render_template('GetNextBusforStop', **options)
	return statement(text).simple_card('GetNextBusforStop', text)

if __name__ == "__main__":
	app.run(debug=True)
