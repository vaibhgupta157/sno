from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
import time
import json


class ConfigDB:

    LOCKED = False
    active_sessions = {}

    def acquire_lock():
        no_of_attempts = 60
        attempts = 1
        while ConfigDB.LOCKED and attempts <= no_of_attempts:
            time.sleep(3)
            attempts += 1
        if attempts > no_of_attempts:
            return {"Error" : "Error while grabbing ConfigDB lock"}
        
        with open("../ConfigDB") as conf:
            data = conf.read()
        
        snoDict = json.loads(data)
        snoDB= sno()
        pybindJSONDecoder.load_json(snoDict, None, None, snoDB)
        ConfigDB.LOCKED = True
        return {"ConfigDB" : snoDB}

    def release_lock():
        ConfigDB.LOCKED = False
        return

    def write(snoRoot, sessionID):
        snoRoot_dict = json.loads(pybindJSON.dumps(snoRoot))
        with open("../ConfigDB", 'w') as conf:
            json.dump(snoRoot_dict, conf)
        ConfigDB.LOCKED = False
        return (ConfigDB.get_session(sessionID))

    def get_session(sessionID=None):
        with open("../ConfigDB") as conf:
            data = conf.read()
        
        snoDict = json.loads(data)
        snoDB= sno()
        pybindJSONDecoder.load_json(snoDict, None, None, snoDB)
        ConfigDB.active_sessions[sessionID] = snoDB
        return snoDB
