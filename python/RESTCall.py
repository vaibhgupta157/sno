import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from device import Device
from sno import sno

app = flask.Flask(__name__)
cors = CORS(app)

#app.config["DEBUG"] = True


@app.route('/api/devices/device', methods=['POST'])
def add_device():
    if not request.json:
        abort(400)
    vars = request.json
    device = Device(vars['name'])
    try:
        snoRoot = device.add(snoRoot, vars)
        return jsonify({"Success" : "Added successfully"}), 201
    except Exception as e:
        return jsonify({"Error" : "Error while adding device to sno :" + str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8100, debug=True)
