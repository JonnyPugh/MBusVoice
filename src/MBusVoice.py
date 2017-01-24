from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

@ask.launch
def launch():
	speech_text = "Hello, welcome to MBus Voice."
	return statement(speech_text)

@ask.intent('GetNextBusforStop')
def hello(StopID):
	print(StopID)
	text = render_template('GetNextBusforStop', StopID=StopID)
	return statement(text).simple_card('GetNextBusforStop', text)

if __name__ == '__main__':
	app.run(debug=True)