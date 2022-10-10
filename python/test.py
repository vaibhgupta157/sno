from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
import pprint
import json
#from deepdiff import DeepDiff
#import dictdiffer  
#from jsondiff import diff
import xmltodict
import xml.etree.ElementTree as ET
from lxml import etree
import re


def convert_to_dict(xml_root, output_dict={}):
    prim_attrib = None
    if xml_root.tag in ["module", "submodule", "belongs-to", "import", "container", "list", "leaf", "leaf-list"]:
        if "name" in xml_root.attrib.keys():
            output_dict[xml_root.attrib['name']] = {}
            output_dict[xml_root.attrib['name']]['yang_type'] = xml_root.tag
            prim_attrib = "name"
        elif "value" in xml_root.attrib.keys():
            output_dict[xml_root.attrib['value']] = {}
            output_dict[xml_root.attrib['value']]['yang_type'] = xml_root.tag
            prim_attrib = "value"
        elif "module" in xml_root.attrib.keys():
            output_dict[xml_root.attrib['module']] = {}
            output_dict[xml_root.attrib['module']]['yang_type'] = xml_root.tag
            prim_attrib = "module"
        for k,v in xml_root.attrib.items():
            if k == prim_attrib:
                continue
            output_dict[xml_root.attrib[prim_attrib]][+k] = v
        for child in xml_root:
            convert_to_dict(child, output_dict[xml_root.attrib[prim_attrib]])
    else:
        for k,v in xml_root.attrib.items():
            if xml_root.tag in output_dict.keys():
                if not isinstance(output_dict[xml_root.tag], list):
                    output_dict[xml_root.tag] = [output_dict[xml_root.tag]]
                output_dict[xml_root.tag].append(v)
            else:
                output_dict[xml_root.tag] = v
        for child in xml_root:
            convert_to_dict(child, output_dict)
        
    
    return output_dict
    
'''
with open("/home/anuta/sno/device/yang/device.yin") as f:
    device_yin = f.read()

device_yin = re.sub(' xmlns="[^"]+"', '', device_yin, count=1)
root = ET.fromstring(device_yin)
op_dict = convert_to_dict(root)
op_dict_str = str(op_dict).replace("\'", "\"")
print (op_dict_str)


with open("/home/anuta/sno/device/yang/config/cumulus-nclu.yin") as f:
    config_yin = f.read()

config_yin = re.sub(' xmlns="[^"]+"', '', config_yin, count=1)
root = ET.fromstring(config_yin)
op_dict = convert_to_dict(root)
op_dict_str = str(op_dict).replace("\'", "\"")
print (op_dict_str)
'''

with open("/home/anuta/sno/device/yang/config/ietf-interfaces@2018-02-20.yin") as f:
    config_yin = f.read()

config_yin = re.sub(' xmlns="[^"]+"', '', config_yin, count=1)
root = ET.fromstring(config_yin)
op_dict = convert_to_dict(root)
op_dict_str = str(op_dict).replace("\'", "\"")
print (op_dict_str)

#print (dict(op_dict_str))
#pp = pprint.PrettyPrinter(indent=2)
#print (pp.pprint(json.dumps(xmltodict.parse(device_yin))))

#print (type(xmltodict.parse(device_yin)))

'''
pp = pprint.PrettyPrinter(indent=4)

test_root = sno()

print(test_root.get(filter=True))

rt = test_root.devices.device.add('TEST')
rt.mgmt_ip = "10.10.10.10"
rt.config.commands.cmd.append('net add swp1 access vlan 20')
test_root.devices.device.add('TEST4')

other_root = sno()
new_rt = other_root.devices.device.add('TEST')
new_rt.mgmt_ip = "10.10.10.10"
new_rt.config.commands.cmd.append('net add swp1 access vlan 20')
new_rt.config.commands.cmd.append('net add swp1 access vlan 10')
new_rt = other_root.devices.device.add('TEST2')
new_rt.mgmt_ip = "10.10.10.11"
new_rt.config.commands.cmd.append('net add swp1 access vlan 10')

new_rt = other_root.devices.device.add('TEST3')
new_rt.mgmt_ip = "10.10.10.11"
new_rt.config.commands.cmd.append('net add swp1 access vlan 10')



t1 = json.loads(pybindJSON.dumps(test_root))
t2 = json.loads(pybindJSON.dumps(other_root))

diff1 = (diff(t1, t2))

print (diff1)

#if 'devices' in diff1.keys() and 'device' in diff1['devices'].keys():
#    for device in diff1['devices']['device'].keys():
#        if 'config' in diff1['devices']['device'][device]:
##            pass

#print ((diff1['devices']['device']))

#ddiff = DeepDiff(t1, t2, ignore_order=True)

#print (ddiff)



print (test_root.devices.device.keys())

print (dir(pybindJSONDecoder))

print (rt.mgmt_ip)
print((json.loads(pybindJSON.dumps(test_root.devices.device['TEST']))))
print(pybindJSONEncoder(test_root))
'''

