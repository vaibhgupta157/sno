from test_yang import test_yang
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
import json

class ConfigHelper(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def print_attr(self, *args, **kwargs):
        for att in self.__dict__:
            print (att, getattr(self, att))

d1 = {"a": 1, "b":2}
configH = ConfigHelper(**d1)
configH.print_attr()
extmethods = {
      '/device/services': configH
}

test1 = test_yang(extmethods=extmethods)
device1 = test1.device.add("test1")
device1 = test1.device["test1"]
print(device1)

config = device1.services._print_attr()

snoDB_dict = json.loads(pybindJSON.dumps(test1))
print((snoDB_dict))
snoDB_dict['device']['test1']['services'] = {}
snoDB_dict['device']['test1']['services']["a"] = 1
snoDB_dict['device']['test1']['services']["b"] = 2
print((snoDB_dict))

snoDB_dict['device']['test1']['services'] = {}
test2 = test_yang(extmethods=extmethods)
pybindJSONDecoder.load_json(snoDB_dict, None, None, test2)
print (test2)
