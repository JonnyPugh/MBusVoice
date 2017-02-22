from flask import Flask, render_template
import controllers
import config 

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

# Register the controllers
app.register_blueprint(controllers.main)
app.register_blueprint(controllers.api_v1.edit_favorites)
app.register_blueprint(controllers.api_v1.get_favorites)
app.register_blueprint(controllers.api_v1.post_favorites)

app.secret_key = "\xe9\x04\xd0\xc2\xab\t\x00\x13\xe2N\xa0\xe3\x90\x83iE\xb7\xa1\xd1\x1cp\x88_\xf9"

@app.errorhandler(403)
def access_forbidden(e):
	return render_template("unauthorized.html"), 403

# Listen on external IPs using the configured port
if __name__ == '__main__':
    app.run(host=config.env['host'], port=config.env['port'], debug=True)
