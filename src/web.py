from flask import Flask, render_template
import controllers

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder="templates")

# Register page controllers
app.register_blueprint(controllers.main)

# Register API controllers
app.register_blueprint(controllers.api_v1.home_blueprint)
app.register_blueprint(controllers.api_v1.destination_blueprint)
app.register_blueprint(controllers.api_v1.groups_blueprint)
app.register_blueprint(controllers.api_v1.order_blueprint)
app.register_blueprint(controllers.api_v1.time_blueprint)
app.register_blueprint(controllers.api_v1.stops_blueprint)

# Set the secret_key so we can use sessions
app.secret_key = "\xe9\x04\xd0\xc2\xab\t\x00\x13\xe2N\xa0\xe3\x90\x83iE\xb7\xa1\xd1\x1cp\x88_\xf9"

@app.errorhandler(401)
def access_forbidden(e):
	return render_template("forbidden.html"), 401

# Listen on external IPs using the configured port
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
