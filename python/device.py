from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
import pprint
import requests, json
from requests.auth import HTTPBasicAuth

ODL_Base_URL = "http://localhost:8181/restconf/config/network-topology:network-topology/topology/topology-netconf/node/"
ODL_USER = "admin"
ODL_PASSWORD = "admin"


class Device(object):

    def __init__(self, name):
        self.name = name

    def add(self, snoRoot, vars):
        if self.name in snoRoot.devices.device.keys():
            raise KeyError(self.name + "already present in device list")
        else:
            tempRoot = sno()
            newDevice = tempRoot.devices.device.add(self.name)
            pybindJSONDecoder.load_json(vars, None, None, newDevice)
            snoRoot.devices.device.append(newDevice)
            return snoRoot

    def update(self, snoRoot, vars):
        if self.name not in snoRoot.devices.device.keys():
            raise KeyError(self.name + "not present in device list")
        else:
            DeviceObj = snoRoot.devices.device[self.name]
            DeviceDict = json.loads(pybindJSON.dumps(DeviceObj, filter=True))
            DeviceDict.update(vars)
            pybindJSONDecoder.load_json(DeviceDict, None, None, DeviceObj)
            return snoRoot

    def delete(self, snoRoot):
        if self.name not in snoRoot.devices.device.keys():
            raise KeyError(self.name + "not present in device list")
        else:
            snoRoot.devices.device.delete(self.name)
            return snoRoot

    def check_sync(self, snoRoot):
        if self.name not in snoRoot.devices.device.keys():
            raise KeyError(self.name + "not present in device list")
        else:
            ConfigObj = snoRoot.devices.device[self.name].config
            get_config_url = ODL_Base_URL + self.name + "/yang-ext:mount/"
            response = requests.get(get_config_url, verify=False, auth=HTTPBasicAuth(ODL_USER, ODL_PASSWORD))
            if response.status_code not in [200, 201, 204]:
                raise Exception(response.text)
            ConfigDict = json.loads(pybindJSON.dumps(ConfigObj, filter=True))
            if ConfigDict == json.loads(response.text): #cmp returns 0 if equal
                return True
            else:
                return False


if __name__ == "__main__":
    snoRoot = sno()
    rt = snoRoot.devices.device.add('Test1')
    rt.mgmt_ip = "10.10.10.10"
    newDevice = Device("test")
    vars = {
        "mgmt_ip" : "192.168.50.134",
        "netconf_port" : 830,
        "device_type" : "CumulusLinux",
        "netconf_user" : "admin",
        "netconf_password" : "admin"
    }
    newsnoRoot = newDevice.add(snoRoot, vars)
    print(pybindJSON.dumps(newsnoRoot))
    print (newDevice.check_sync(snoRoot))