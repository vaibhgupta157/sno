from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
import pprint
import json
#from deepdiff import DeepDiff
#import dictdiffer  
from jsondiff import diff


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