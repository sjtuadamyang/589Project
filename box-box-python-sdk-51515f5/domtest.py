#!/usr/bin/python

import types
import boxdotnet
from xml.dom.minidom import Document

def object_convert(inst):
    doc = Document()
    view = doc.createElement("view")
    doc.appendChild(view)


"""
    builder.startElement(inst.__class__.__name__)

    for attr in inst.__dict__.keys():
        if attr[0] == '_':
            continue
        value = getattr(inst, attr)
        if type(value) == types.InstanceType:
            object_convert(builder, value)
        else:
            builder.startElement(attr)
            builder.text(str(value))
            builder.endElement(attr)

    builder.endElement(inst.__class__.__name__)
"""

if __name__=='__main__':
    test = boxdotnet.XMLNode()
    test.attr1 = [] 
    test.attr1[0] = 123
    test.attr1[1] = {'at':'12', 'python':'py'}
    builder = Builder()
    object_convert(builder, test)

