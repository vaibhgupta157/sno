import flask
from flask import request, jsonify, render_template, redirect, url_for, flash
#from flask_cors import CORS, cross_origin
from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
from ConfigDB import ConfigDB
import random
import json
import subprocess, os
import commitManager 
import jinja2

app = flask.Flask(__name__)
app.secret_key = "super secret key"
app.config["DEBUG"] = True
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
            flash("User not found. Please try again!!")
            return redirect(url_for('login'))
        elif users[user]['password'] != password:
            flash("Invalid Username or Password. Please try again!!")
            return redirect(url_for('login'))
        response = redirect(url_for("home"))

        sessionCookie = "sno" + user + str(random.randint(1001, 5000))
        count = 0
        while sessionCookie in ConfigDB.active_sessions.keys() and count<100:
            sessionCookie = "sno" + user + random.randint(1001, 5000)
            count += 1
        if count == 100:
            flash("Session count limit reached. Please try after sometime!!")
            return redirect(url_for('login'))
        snoDict = ConfigDB.get_session(sessionID=sessionCookie)
        #active_sessions[sessionCookie] = snoDB
        response.set_cookie('SessionCookie', sessionCookie)
        return response
    else:
        return render_template('login.html')

@app.route('/devices/device', methods=["GET", "POST"])
def add_device():
    session_id = request.cookies.get('SessionCookie')
    snoDB_dict = ConfigDB.active_sessions[session_id]
    if request.method == 'GET':
        #snoDB_dict = json.loads(pybindJSON.dumps(snoDB.devices.device))
        devices_dict = snoDB_dict['devices']['device']
        jtox_output, jtox_error = subprocess_cmd("pyang -f jtox ../yang/sno.yang ../device/yang/device.yang ../device/yang/*/*.yang")
        #print ((jtox_output).decode('utf-8'))
        tree_output = json.loads(jtox_output.decode('utf-8'))
        devices_dict['tree'] = tree_output['tree']
        print (devices_dict)
        return render_template('getlistdevice.html', snoDB_dict=devices_dict)

    new_device_dict = request.form.to_dict()
    #session_id = request.cookies.get('SessionCookie')
    #snoDB = ConfigDB.active_sessions[session_id]
    snoDB_dict['devices']['device'][new_device_dict['name']] = new_device_dict
    #new_device = snoDB.devices.device.add(device_dict['name'])
    #pybindJSONDecoder.load_json(device_dict, None, None, new_device)
    ConfigDB.active_sessions[session_id] = snoDB_dict
    flash("Device added successfully")
    return redirect(url_for('add_device'))


@app.route('/devices/device/<device>', methods=["GET", "POST"])
def edit_device(device):
    session_id = request.cookies.get('SessionCookie')
    snoDB_dict = ConfigDB.active_sessions[session_id]
    deviceObj_dict = snoDB_dict['devices']['device'][device]
    if request.method == 'GET':
        #device_dict = json.loads(pybindJSON.dumps(deviceObj))
        #device_type = deviceObj_dict["device_type"]
        with open("/home/anuta/sno/device/yang/device_json") as f:
            device_json = json.load(f)        
        #jtox_cmd_config_yang = "pyang -f jtox ../yang/sno.yang ../device/yang/device.yang ../device/yang/" + str(device_type) + "/cumulus-nclu.yang"
        #jtox_output, jtox_error = subprocess_cmd(jtox_cmd_config_yang)
        #tree_output = json.loads(jtox_output.decode('utf-8'))
        deviceObj_dict['tree'] = device_json['device']['devices']['device']
        print (deviceObj_dict)
        return render_template('editDevice.html', device_dict=deviceObj_dict)
        


    device_dict = request.form.to_dict()
    correct_nested_dict(device_dict)
    if "_method" in device_dict.keys():
        del snoDB_dict["devices"]["device"][device]
        #snoDB.devices.device.delete(device)
        ConfigDB.active_sessions[session_id] = snoDB_dict
        flash("Device deleted successfully")
        return redirect(url_for('add_device'))
    #session_id = request.cookies.get('SessionCookie')
    #snoDB = ConfigDB.active_sessions[session_id]
    #device = snoDB.devices.device[device]
    deviceObj_dict.update(device_dict)
    #pybindJSONDecoder.load_json(device_dict, None, None, deviceObj)
    ConfigDB.active_sessions[session_id] = snoDB_dict
    flash("Device edited successfully")
    return redirect(url_for('add_device'))


@app.route('/devices/device/<device>/<module>', methods=["GET", "POST"])
def edit_module(device, module):
    session_id = request.cookies.get('SessionCookie')
    snoDB_dict = ConfigDB.active_sessions[session_id]
    moduleObj_dict = snoDB_dict['devices']['device'][device]["config"][module]
    if request.method == 'GET':
        #device_dict = json.loads(pybindJSON.dumps(deviceObj))
        #device_type = deviceObj.device_type
        with open("/home/anuta/sno/device/yang/config/"+module+"_json") as f:
            module_json = json.load(f)
        module_striped = module
        if "@" in module: 
            module_striped = module[:module.find("@")]     
        print (module_striped)
        #jtox_cmd_config_yang = "pyang -f jtox ../yang/sno.yang ../device/yang/device.yang ../device/yang/" + str(device_type) + "/cumulus-nclu.yang"
        #jtox_output, jtox_error = subprocess_cmd(jtox_cmd_config_yang)
        #tree_output = json.loads(jtox_output.decode('utf-8'))
        del module_json[module_striped]["yang_type"]
        #del module_json[module_striped]["yang_version"]
        del module_json[module_striped]["namespace"]
        del module_json[module_striped]["prefix"]
        del module_json[module_striped]["revision"]
        moduleObj_dict['tree'] = module_json[module_striped]
        print (moduleObj_dict)
        return render_template('editModule.html', module_dict=moduleObj_dict, device=device, module=module)
        


    device_dict = request.form.to_dict()
    correct_nested_dict(device_dict)
    if "_method" in device_dict.keys():
        snoDB.devices.device.delete(device)
        ConfigDB.active_sessions[session_id] = snoDB
        flash("Device deleted successfully")
        return redirect(url_for('add_device'))
    #session_id = request.cookies.get('SessionCookie')
    #snoDB = ConfigDB.active_sessions[session_id]
    #device = snoDB.devices.device[device]
    pybindJSONDecoder.load_json(device_dict, None, None, deviceObj)
    ConfigDB.active_sessions[session_id] = snoDB
    flash("Device edited successfully")
    return redirect(url_for('add_device'))


@app.route('/home', methods=["GET"])
def home():
    session_id = request.cookies.get('SessionCookie')
    try:
        snoDB_dict = ConfigDB.active_sessions[session_id]
    except KeyError as e:
        flash("Invalid session ID. Please login again!!")
        return redirect(url_for('login'))
    #snoDB_dict = json.loads(pybindJSON.dumps(snoDB))
    jtox_output, jtox_error = subprocess_cmd("pyang -f jtox ../yang/sno.yang ../device/yang/device.yang ../device/yang/*/*.yang")
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
        flash ("Commit Dry Run: \n" + DryRun_response)
    else:
        try:
            committedDB_dict = commitManager.commit(snoDB, session_id)
        except Exception as e:
            flash ("Error while doing commit: " + str(e))
        if 'Error' in committedDB_dict.keys():
            flash ("Error while doing commit: " + committedDB_dict['Error'])
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8100, debug=True)
