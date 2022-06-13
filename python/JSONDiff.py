import json
from sno import sno
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONEncoder, pybindJSONDecoder
from pyangbind.lib.serialise import pybindIETFXMLEncoder, pybindIETFXMLDecoder
from lxml import etree

def calculate_diff(left, right, snoObject=sno()):
    left_dict = json.loads(pybindJSON.dumps(left))
    right_dict = json.loads(pybindJSON.dumps(right))


    right_side_recursion(left_dict, right_dict)

    left_after_right_recursion = snoObject

    pybindJSONDecoder.load_json(left_dict, None, None, left_after_right_recursion)

    left_xml = (pybindIETFXMLEncoder.serialise(left_after_right_recursion))
    right_xml = (pybindIETFXMLEncoder.serialise(right))
    root_left = etree.fromstring(left_xml)
    root_right = etree.fromstring(right_xml)

    left_side_recursion(root_left, root_right)
    return (etree.tostring(root_left).decode())



def right_side_recursion(left_dict, right_dict):
    
    for key in right_dict.keys():
        if key not in left_dict.keys():
            left_dict[key] = right_dict[key]
        elif left_dict[key] == right_dict[key]:
            del left_dict[key]
        elif isinstance(right_dict[key], dict):
            right_side_recursion(left_dict[key], right_dict[key])
        elif isinstance(right_dict[key], list):
            for item in right_dict[key]:
                if item not in left_dict[key]:
                    left_dict[key].append(item)
                else:
                    left_dict[key].remove(item)
        elif left_dict[key] != right_dict[key]:
            left_dict[key] = right_dict[key]
        

def JSONDiff(left, right):
    #left_side_recursion(left, right)
    print (left)
    print (right)

''' 
def left_side_recursion(left, right):
    for key in left.keys():
        if key not in right.keys():
            left[key]['@operation'] = 'delete'
            return
        elif isinstance(left[key], dict):
            left_side_recursion(left[key], right[key])
        elif isinstance(left[key], list):
            for i in range(len(left[key])):
                if left[key][i] != right[key][i]:
                    left[key][i]['@operation'] = 'delete'
            return
'''

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