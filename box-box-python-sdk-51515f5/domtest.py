#!/usr/bin/python

import types
import boxdotnet
from xml.dom.minidom import Document

def object_convert(inst):
    def __recursive_create(doc, base, inst):
        #convert the inst into a dom and append to base
        element = doc.createElement(inst.elementName)
        base.appendChild(element)
        for ab in inst.attrib.keys():
            element.setAttribute(ab, inst.attrib[ab])
        for an in inst.__dict__.keys():
            attr = inst.__dict__[an]
            if isinstance(attr, list) and isinstance(attr[0], boxdotnet.XMLNode):
                #recursively call the function
                for child in attr:
                    __recursive_create(doc, element, child)
    doc = Document()
    __recursive_create(doc, doc, inst) 
    return doc.toprettyxml(indent="    ")

if __name__=='__main__':
    f = open('./viewmeta.xml', 'rb')
    test = boxdotnet.XMLNode.parseXML(f.read())
    xmlstr = object_convert(test.view[0])
    print xmlstr
    f.close()

