
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
from lxml import etree
import xml.etree.ElementTree as ET
import xmltodict


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


class nsmapeditor:

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def remove_namespace(self):
        self.nsmap_dict = {}
        root = etree.fromstring(self.left)
        # Remove namespace prefixes
        for elem in root.getiterator():
            elem.tag = etree.QName(elem).localname
            for k,v in elem.nsmap.items():
                if v not in self.nsmap_dict.values():
                    self.nsmap_dict[etree.QName(elem).localname] = v
        # Remove unused namespace declarations
        etree.cleanup_namespaces(root)
        self.striped_left = etree.tostring(root).decode()

        root = etree.fromstring(self.right)
        # Remove namespace prefixes
        for elem in root.getiterator():
            elem.tag = etree.QName(elem).localname
            for k,v in elem.nsmap.items():
                if v not in self.nsmap_dict.values():
                    self.nsmap_dict[etree.QName(elem).localname] = v
        # Remove unused namespace declarations
        etree.cleanup_namespaces(root)
        self.striped_right = etree.tostring(root).decode()
    
    def add_namespace(self, xml_string):
        root = etree.fromstring(xml_string)

        for elem in root.getiterator():
            if elem.tag in self.nsmap_dict.keys():

                real_tag = elem.tag

                #elem.tag = '{' + self.nsmap_dict[real_tag] + '}' + real_tag
                #elem.tag = etree.QName(elem).localname

                elem.set("xmlns", self.nsmap_dict[real_tag])

        etree.cleanup_namespaces(root)
        return (etree.tostring(root).decode())

    def add_namespace_xml(self, xml_string):
        root = ET.fromstring(xml_string)

        #print (dir(ET.tostring))

        for elem in root.getiterator():
            if elem.tag in self.nsmap_dict.keys():

                real_tag = elem.tag

                #ET.register_namespace("", local_nsmap_dict[real_tag])
                
                elem.tag = '{' + self.nsmap_dict[real_tag] + '}' + real_tag

                #elem.set("xmlns", self.nsmap_dict[real_tag])
                print (dir(elem))

        
        return (ET.tostring(root).decode())

def xml_remove_namespaces(xml_string):
    root = etree.fromstring(xml_string)

    # Remove namespace prefixes
    for elem in root.getiterator():
        elem.tag = etree.QName(elem).localname
    # Remove unused namespace declarations
    etree.cleanup_namespaces(root)

    return (etree.tostring(root).decode())

def commit(originalsnoRoot, snoRoot, DryRun=False):
    #with open("ConfigDB", "r") as f:
    #    originalsno_dict = json.loads(f.read())

    formatter = SNOFormatter(normalize=formatting.WS_BOTH)
    #formatter = formatting.XMLFormatter(normalize=formatting.WS_TEXT)

    if DryRun:
        original_xml = (pybindIETFXMLEncoder.serialise(originalsnoRoot))
        new_xml = (pybindIETFXMLEncoder.serialise(snoRoot))
        namespace_editor = nsmapeditor(original_xml, new_xml)                
        namespace_editor.remove_namespace()
        diff_xml = (main.diff_texts(namespace_editor.striped_left, namespace_editor.striped_right, formatter=formatter, diff_options={'F': 1}))
        diff_xml = namespace_editor.add_namespace(diff_xml)
        print (diff_xml)
        return

    sno_dict = json.loads(pybindJSON.dumps(snoRoot))
    originalsno_dict = json.loads(pybindJSON.dumps(originalsnoRoot))
    difference = diff(originalsno_dict, sno_dict)



    #print ((originalsnoRoot.get()))
    if 'devices' in difference.keys() and 'device' in difference['devices'].keys():
        for device in difference['devices']['device'].keys():
            if 'config' in difference['devices']['device'][device]:
                config_dict = difference['devices']['device'][device]['config']
                #print ((originalsnoRoot.devices.device[device].config.get()))

                #print (config_dict)


                original_config = (pybindIETFXMLEncoder.serialise(originalsnoRoot.devices.device[device].config))
                new_config = (pybindIETFXMLEncoder.serialise(snoRoot.devices.device[device].config))

                namespace_editor = nsmapeditor(original_config, new_config)
                
                namespace_editor.remove_namespace()

                #print (main.diff_texts(original_config, new_config))
                #print (main.diff_texts(original_config, new_config, formatter=formatter))
                #print (main.diff_texts(original_config, new_config, diff_options={'F': 1.0}))
                diff_xml = (main.diff_texts(namespace_editor.striped_left, namespace_editor.striped_right, formatter=formatter, diff_options={'F': 1}))

                diff_xml = namespace_editor.add_namespace(diff_xml)
                #diff_xml = xml_remove_namespaces(diff_xml)
                print (diff_xml)
                diff_object = pybindIETFXMLDecoder.decode(diff_xml, snoRoot.devices.device[device], 'config')
                print (diff_object)


    

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
    #new_rt.config.commands.cmd.append('test2')
    new_rt = other_root.devices.device.add('TEST2')
    new_rt.mgmt_ip = "10.10.10.11"
    new_rt.config.commands.cmd.append('net add swp1 access vlan 10')

    new_rt = other_root.devices.device.add('TEST3')
    new_rt.mgmt_ip = "10.10.10.11"
    new_rt.config.commands.cmd.append('net add swp1 access vlan 10')

    commit(test_root, other_root, DryRun=True)
    commit(test_root, other_root)
