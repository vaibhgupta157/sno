from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
import pprint
import json
from jsondiff import diff
from jsondiff.symbols import *
from deviceTransaction import device_push
from xmldiff import formatting, main
from SNOFormatter import SNOFormatter


class parseConfig:

    def __init__(self, original_config, new_config):
        self.original_config = original_config
        self.new_config = new_config
        #self.diff_dict = diff_dict
        self.result_dict = {}

    def parse(self, diff_dict, result_dict):
        if isinstance(diff_dict, dict):
            for key in diff_dict.keys():
                if isinstance(diff_dict[key], dict):
                    result_dict[key] = diff_dict[key]



def parseConfig(config_dict):
    tempsno = sno()
    tempdevice = tempsno.devices.device.add['TEST']
    tempConfig = tempdevice.config
    if isinstance(config_dict, dict):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                for newkey, newvalue in value.items():
                    if newkey == 'insert':
                        config_dict[key] = newvalue[1]


def commit(originalsnoRoot,snoRoot):
    #with open("ConfigDB", "r") as f:
    #    originalsno_dict = json.loads(f.read())

    print (dir(formatting.XMLFormatter))
    formatter = SNOFormatter(normalize=formatting.WS_BOTH)
    #formatter = formatting.XMLFormatter(normalize=formatting.WS_BOTH)
    sno_dict = json.loads(pybindJSON.dumps(snoRoot))
    originalsno_dict = json.loads(pybindJSON.dumps(originalsnoRoot))
    difference = diff(originalsno_dict, sno_dict)
    print ((originalsnoRoot.get()))
    if 'devices' in difference.keys() and 'device' in difference['devices'].keys():
        for device in difference['devices']['device'].keys():
            if 'config' in difference['devices']['device'][device]:
                config_dict = difference['devices']['device'][device]['config']
                #print ((originalsnoRoot.devices.device[device].config.get()))
                print (device)
                print (config_dict)
                original_config = (pybindIETFXMLEncoder.serialise(originalsnoRoot.devices.device[device].config))
                new_config = (pybindIETFXMLEncoder.serialise(snoRoot.devices.device[device].config))
                print (original_config)
                print (new_config)
                print (main.diff_texts(original_config, new_config))
                print (main.diff_texts(original_config, new_config, formatter=formatter, diff_options={'F': 1.0}))


    

    #originalsnoRoot = sno()
    pybindJSONDecoder.load_json(originalsno_dict, None, None, originalsnoRoot)

if __name__ == "__main__":
    test_root = sno()
    rt = test_root.devices.device.add('TEST')
    rt.mgmt_ip = "10.10.10.10"
    #rt.config.commands.cmd.append('net add swp1 access vlan 20')
    #rt.config.commands.cmd.append('net add swp1 access vlan 30')
    #rt.config.commands.cmd.append('net add swp1 access vlan 40')
    rt.config.commands.cmd.append('test1')
    rt.config.commands.cmd.append('test2')
    rt.config.commands.cmd.append('test3')
    test_root.devices.device.add('TEST4')

    other_root = sno()
    new_rt = other_root.devices.device.add('TEST')
    new_rt.mgmt_ip = "10.10.10.10"
    #new_rt.config.commands.cmd.append('net add swp1 access vlan 20')
    #new_rt.config.commands.cmd.append('net add swp1 access vlan 10')
    new_rt.config.commands.cmd.append('test1')
    new_rt.config.commands.cmd.append('test4')
    new_rt.config.commands.cmd.append('adfdf')
    new_rt = other_root.devices.device.add('TEST2')
    new_rt.mgmt_ip = "10.10.10.11"
    new_rt.config.commands.cmd.append('net add swp1 access vlan 10')

    new_rt = other_root.devices.device.add('TEST3')
    new_rt.mgmt_ip = "10.10.10.11"
    new_rt.config.commands.cmd.append('net add swp1 access vlan 10')

    commit(test_root, other_root)
