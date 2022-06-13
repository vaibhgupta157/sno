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


