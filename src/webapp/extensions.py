from flask import jsonify

def verify_json_parameters(parameters, json):
    for parameter in parameters:
        if parameter not in json:
            return jsonify({"errors": [{"message": "You did not provide the necessary fields"}]}), 400
    return None