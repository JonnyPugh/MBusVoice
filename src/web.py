from flask import Flask, render_template
import controllers

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

# Register the controllers
app.register_blueprint(controllers.main)

# Register API controllers
app.register_blueprint(controllers.api_v1.destination_endpoint)
app.register_blueprint(controllers.api_v1.home_endpoint)
app.register_blueprint(controllers.api_v1.min_time_endpoint)
app.register_blueprint(controllers.api_v1.nicknames_endpoint)
app.register_blueprint(controllers.api_v1.order_endpoint)

app.secret_key = "\xe9\x04\xd0\xc2\xab\t\x00\x13\xe2N\xa0\xe3\x90\x83iE\xb7\xa1\xd1\x1cp\x88_\xf9"

@app.errorhandler(403)
def access_forbidden(e):
	return render_template("unauthorized.html"), 403

# Listen on external IPs using the configured port
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000, debug=True)
