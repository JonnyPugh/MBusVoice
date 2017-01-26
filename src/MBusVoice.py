from flask import Flask, render_template
from flask_ask import Ask, statement

from mbus_api_wrapper import *

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def launch():
	speech_text = "Hello, welcome to MBus Voice."
	return statement(speech_text)

@ask.intent('GetNextBusforStop')
def hello(StopID):
	estimated_times = get_buses_for_stop(StopID)[0]
	options = {
		'stopid': StopID,
		'minutes': estimated_times['avg'],
		'busline': routes[estimated_times['route']]
	}
	text = render_template('GetNextBusforStop', **options)
	return statement(text).simple_card('GetNextBusforStop', text)

if __name__ == '__main__':
	app.run(debug=True)