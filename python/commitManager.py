
from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
import pprint
import json
from jsondiff import diff
from jsondiff.symbols import *
from deviceTransaction import NetworkTransaction
#from xmldiff import formatting, main
#from SNOFormatter import SNOFormatter
from lxml import etree
import xml.etree.ElementTree as ET
import xmltodict
import difflib
from ConfigDB import ConfigDB
from JSONDiff import calculate_diff

def XMLDiff(left, right):
    root_left = etree.fromstring(left)
    root_right = etree.fromstring(right)

    tree = etree.ElementTree(root_right)
    
    #etree.register_namespace("nc", "urn:ietf:params:xml:ns:netconf:base:1.0")

    left_side_recursion(root_left, root_right)
    right_side_recursion(root_left, root_right)

    return (etree.tostring(root_left).decode())

def left_side_recursion(root_left, root_right): 


    if root_left.tag != root_right.tag:
        if not root_right.findall('.//' + root_left.tag):
            root_left.set("operation", "delete")
            for element in root_left.getchildren():
                root_left.remove(element)
            return
        else:
            all_matches = root_right.findall('.//' + root_left.tag)
            all_matches_text = [elem.text for elem in all_matches]
            if root_left.text not in all_matches_text:
                root_left.set("operation", "delete")
                for element in root_left.getchildren():
                    root_left.remove(element)
                return
            else:
                for element in root_left.getchildren():
                    left_side_recursion(element, root_right)
    else:
        if root_left.text != root_right.text:
            root_left.set("operation", "delete")
            return
        else:
            for element in root_left.getchildren():
                left_side_recursion(element, root_right)

def right_side_recursion(root_left, root_right):

    #for element in root_right.getchildren():
    for element in root_right.getchildren():
        if not root_left.findall(element.tag):
            print ("Did not find element tag. so appending")
            print (element.tag)
            print (element.text)
            root_left.append(element)
        else:
            all_matches = root_left.findall(element.tag)
            all_matches_string = [etree.tostring(elem) for elem in all_matches]
            all_matches_text = [elem.text for elem in all_matches]
            if etree.tostring(element) not in all_matches_string:
                best_match = find_best_match(all_matches, element)
                if best_match:
                    right_side_recursion(best_match, element)
                else:
                    print ("Did not find best match")
                    print (element.tag)
                    print (element.text)
                    root_left.append(element)
                    '''
                    for elem in all_matches:
                        if elem.text == element.text:
                            break
                    right_side_recursion(elem, element)
                    '''
    else:
        return

def compare_element(left_element, right_element, depth=0):


    if left_element.tag == right_element.tag and left_element.text == right_element.text:
        depth += 1

    
    print ("inside compare element")
    
    for x,y in zip(left_element, right_element):
        print (x)
        print (y)

    #print (etree.tostring(left_element))
    for i in range(len(right_element)):
        if i >= len(left_element):
            break
        if etree.tostring(left_element[i]) == etree.tostring(right_element[i]):
            depth += 1

    return depth

def find_best_match(all_matches, element):
    best_match = None
    best_depth = 0


    for match in all_matches:
        depth = 0
        #depth = compare_element(match, element)
        for elem_child in element.getchildren():
            for match_child in match.getchildren():
                if elem_child.tag == match_child.tag and elem_child.text == match_child.text:
                    depth += 1
                    break
            else:
                break
            '''
            for elem_child in element.getchildren():
                if match_child.tag == elem_child.tag and match_child.text == elem_child.text:
                    print (elem_child.tag)
                    print (elem_child.text)
                    depth += 1
                    break
            '''
        '''
        for match_child in match.getchildren():
            for elem_child in element.getchildren():
                if etree.tostring(match_child) == etree.tostring(elem_child):
                    depth += 1
                    break
        '''
        
        if depth > best_depth:
            best_depth = depth
            best_match = match

    return best_match
        






def commit(snoRoot, sessionID, DryRun=False):
    #with open("ConfigDB", "r") as f:
    #    originalsno_dict = json.loads(f.read())

    get_lock = ConfigDB.acquire_lock()

    if 'Error' in get_lock.keys():
        return get_lock
    else:
        originalsnoRoot = get_lock['ConfigDB']
  
    if DryRun:
        '''
        original_xml = (pybindIETFXMLEncoder.serialise(originalsnoRoot))
        new_xml = (pybindIETFXMLEncoder.serialise(snoRoot))
        diff_xml = XMLDiff(original_xml, new_xml)
        '''

        diff_xml = calculate_diff(originalsnoRoot, snoRoot)
        ConfigDB.release_lock()
        return diff_xml

    sno_dict = json.loads(pybindJSON.dumps(snoRoot))
    originalsno_dict = json.loads(pybindJSON.dumps(originalsnoRoot))
    difference = diff(originalsno_dict, sno_dict)


    #print ((originalsnoRoot.get()))
    device_config = {}
    if 'devices' in difference.keys() and 'device' in difference['devices'].keys():
        for device in difference['devices']['device'].keys():
            if 'config' in difference['devices']['device'][device]:
                config_dict = difference['devices']['device'][device]['config']
                #print ((originalsnoRoot.devices.device[device].config.get()))

                #print (config_dict)

                if device not in originalsnoRoot.devices.device.keys():
                    return {"Error" : "Device {} not present in DB. First add the device".format(device)}

                
                original_config = originalsnoRoot.devices.device[device].config
                new_config = snoRoot.devices.device[device].config

                '''
                print (original_config)
                print (new_config)
                XMLDiff1 = XMLDiff(original_config, new_config)

                print (XMLDiff1+"\n")
                configXML_tree = list( etree.fromstring(XMLDiff1) )[0]
                configXML = etree.tostring(configXML_tree).decode()

                configXML = "<config>\n" + configXML + "</config>"
                '''


                XMLDIFF = calculate_diff(original_config, new_config, snoObject=originalsnoRoot.devices.device[device].config)

                configXML_tree = list(etree.fromstring(XMLDIFF))[0]
                configXML = etree.tostring(configXML_tree).decode()

                configXML = "<config>\n" + configXML + "</config>"
                print (configXML)


                rev_XMLDIFF = calculate_diff(new_config, original_config, snoObject=originalsnoRoot.devices.device[device].config)
                rev_XML_tree = list(etree.fromstring(rev_XMLDIFF))[0]
                rev_XML = etree.tostring(rev_XML_tree).decode()

                rev_XML = "<config>\n" + rev_XML + "</config>"

                device_config[device]['config'] = configXML
                device_config[device]['rev_config'] = rev_XML


    if device_config:
        try:
            NetworkTransaction(device_config, originalsnoRoot)
        except Exception as e:
            return ({"Error" : "Failed to commit. " + str(e)})

    
    return ({"ConfigDB" : ConfigDB.write(snoRoot, sessionID)})

    #originalsnoRoot = sno()
    #pybindJSONDecoder.load_json(originalsno_dict, None, None, originalsnoRoot)

if __name__ == "__main__":
    test_root = sno()
    rt = test_root.devices.device.add('TEST')
    rt.mgmt_ip = "192.168.50.134"
    rt.netconf_port = 8300
    rt.netconf_user = "admin"
    #rt.netconf_password = "CumulusLinux!"
    rt.netconf_password = "admin"
    rt.config.commands.cmd.append('net add interface swp1 ip address 10.1.1.1/24')
    rt.config.commands.cmd.append('net add interface swp2 ip address 10.2.1.1/24')
    rt.config.commands.cmd.append('net add interface swp3 ip address 10.3.1.1/24')
    #rt.config.commands.cmd.append('test1')
    #rt.config.commands.cmd.append('test2')
    #rt.config.commands.cmd.append('test3')
    test_root.devices.device.add('TEST4')

    test_root_dict = json.loads(pybindJSON.dumps(test_root))
    with open("../ConfigDB", 'w') as conf:
        json.dump(test_root_dict, conf)

    other_root = sno()
    new_rt = other_root.devices.device.add('TEST')
    new_rt.mgmt_ip = "192.168.50.134"
    new_rt.netconf_port = 8300
    new_rt.netconf_user = "admin"
    new_rt.netconf_password = "admin"
    new_rt.config.commands.cmd.append('net add interface swp1 ip address 20.1.1.1/24')
    new_rt.config.commands.cmd.append('net add interface swp2 ip address 20.2.1.1/24')
    #new_rt.config.commands.cmd.append('test1')
    #new_rt.config.commands.cmd.append('test4')
    new_rt.config.commands.cmd.append('net add interface swp3 ip address 20.3.1.1/24')
    #new_rt.config.commands.cmd.append('test2')

    '''
    new_rt = other_root.devices.device.add('TEST2')
    new_rt.mgmt_ip = "10.10.10.11"
    new_rt.config.commands.cmd.append('net add swp1 access vlan 10')

    new_rt = other_root.devices.device.add('TEST3')
    new_rt.mgmt_ip = "10.10.10.11"
    new_rt.config.commands.cmd.append('net add swp1 access vlan 10')
    '''

    print (commit(other_root, DryRun=True))
    print (commit(other_root))
