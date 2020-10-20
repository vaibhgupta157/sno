import flask
from flask import request, jsonify, render_template, redirect, url_for
#from flask_cors import CORS, cross_origin
from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
from ConfigDB import ConfigDB
import random
import json
import subprocess, os
import commitManager 

app = flask.Flask(__name__)
#cors = CORS(app)

#app.config["DEBUG"] = True

users = {'admin' : {'password' : 'admin', 'role' : 'Administrator'}, 'operator' : {'password' : 'operator', 'role' : 'operator'}}



'''
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
'''

def correct_nested_dict(input_dict):

    for key in list(input_dict):
        if '.' in key and '[' in key:
            if key.find('.') < key.find('['):
                if key[:key.find('.')] not in input_dict.keys():
                    input_dict[key[:key.find('.')]] = {}
                input_dict[key[:key.find('.')]][key[key.find('.')+1:]] = input_dict[key]
                del input_dict[key]
                correct_nested_dict(input_dict[key[:key.find('.')]])
            else:
                if key[:key.find('[')] not in input_dict.keys():
                    input_dict[key[:key.find('[')]] = []
                if key[-1] == ']':
                    input_dict[key[:key.find('[')]].append(input_dict[key])
                    del input_dict[key]
                else:
                    new_dict = {}
                    new_dict[key[key.find('.')+1:]] = input_dict[key]
                    input_dict[key[:key.find('[')]].append(new_dict)
                    del input_dict[key]
                    correct_nested_dict(input_dict[key[:key.find('[')]][-1])
        elif '.' in key:
            if key[:key.find('.')] not in input_dict.keys():
                input_dict[key[:key.find('.')]] = {}
            input_dict[key[:key.find('.')]][key[key.find('.')+1:]] = input_dict[key]
            del input_dict[key]
            correct_nested_dict(input_dict[key[:key.find('.')]])
        elif '[' in key:
            if key[:key.find('[')] not in input_dict.keys():
                input_dict[key[:key.find('[')]] = []
            input_dict[key[:key.find('[')]].append(input_dict[key])
            del input_dict[key]
        elif isinstance(input_dict[key], dict):
            correct_nested_dict(input_dict[key])
        elif isinstance(input_dict[key], list):
            for item in input_dict[key]:
                if isinstance(item, dict):
                    correct_nested_dict(item)

def subprocess_cmd(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    proc_stdout, proc_error = process.communicate()
    return proc_stdout.strip(), proc_error

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form['user']
        password = request.form['password']
        global users
        if user not in users.keys():
            return redirect(url_for('login'))
        elif users[user]['password'] != password:
            return redirect(url_for('login'))
        response = redirect(url_for("home"))

        sessionCookie = "sno" + user + str(random.randint(1001, 1100))
        count = 0
        while sessionCookie in ConfigDB.active_sessions.keys() and count<100:
            sessionCookie = "sno" + user + random.randint(1001, 1100)
            count += 1
        if count == 100:
            return redirect(url_for('login'))
        snoDB = ConfigDB.get_session(sessionID=sessionCookie)
        #active_sessions[sessionCookie] = snoDB
        response.set_cookie('SessionCookie', sessionCookie)
        return response
    else:
        return render_template('login.html')

@app.route('/devices/device', methods=["POST"])
def add_device():
    device_dict = request.form.to_dict()
    session_id = request.cookies.get('SessionCookie')
    snoDB = ConfigDB.active_sessions[session_id]
    new_device = snoDB.devices.device.add(device_dict['name'])
    pybindJSONDecoder.load_json(device_dict, None, None, new_device)
    ConfigDB.active_sessions[session_id] = snoDB
    return redirect(url_for('home'))


@app.route('/devices/device/<device>', methods=["POST"])
def edit_device(device):
    device_dict = request.form.to_dict()
    correct_nested_dict(device_dict)
    session_id = request.cookies.get('SessionCookie')
    snoDB = ConfigDB.active_sessions[session_id]
    device = snoDB.devices.device[device]
    pybindJSONDecoder.load_json(device_dict, None, None, device)
    ConfigDB.active_sessions[session_id] = snoDB
    return redirect(url_for('home'))



@app.route('/home', methods=["GET"])
def home():
    session_id = request.cookies.get('SessionCookie')
    snoDB = ConfigDB.active_sessions[session_id]
    snoDB_dict = json.loads(pybindJSON.dumps(snoDB))
    jtox_output, jtox_error = subprocess_cmd("pyang -f jtox ../yang/sno.yang ../device/yang/*")
    #print ((jtox_output).decode('utf-8'))
    tree_output = json.loads(jtox_output.decode('utf-8'))
    snoDB_dict['tree'] = tree_output['tree']
    print (snoDB_dict)
    return render_template('home.html', snoDB_dict=snoDB_dict)

@app.route('/commit', methods=["POST"])
def commit():
    session_id = request.cookies.get('SessionCookie')
    input_dict = request.form.to_dict()
    snoDB = ConfigDB.active_sessions[session_id]
    if 'DryRun' in input_dict.keys():
        DryRun_response = commitManager.commit(snoDB, session_id, DryRun=input_dict['DryRun'])
        print (DryRun_response)
    else:
        committedDB_dict = commitManager.commit(snoDB, session_id)
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8100, debug=True)
