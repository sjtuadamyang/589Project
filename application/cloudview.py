#!/usr/bin/python

import boxdotnet
import gdr_yyt
import os.path

class cloudview:
    client_gd = gdr_yyt.GOOGLE_VIEW()
    client_box = boxdotnet.BoxDotNet()
    metadata = ''
    def __init__(self):
        try:
            f = open('./metadata.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            print "local view is at stamp: "+str(self.metadata.view[0]['ts'])
        except IOError:
            print 'no file named metadata.xml'

    def sync(self):
        """not implemented yet"""
        #download newest metadata
        client_gd.retrieve_metadata()
        #compare  metas
        if self.metadata.view[0] == 0:
            self.metadata = client_gd.metadata
        #while loop starts
        """create folder"""
        """compare metadata lists, choose to upload or download according to the timestamp"""
              

    def init(self):
        """all the client do authentication"""
        if not self.client_box.authenticated:
            self.client_box.authenticate()
        if not self.client_gd.Drive_Service:
            self.client_gd.authent()

        if self.metadata == '':
            #init a empty metadata file
            """
            <metadata>
                <view ts='0'/>
            </metadata>
            """
            self.metadata = boxdotnet.XMLNode()
            self.metadata.elementName='metadata'
            child = boxdotnet.XMLNode()
            child.elementName = 'view'
            child['ts']='0'
            try:
                list = getattr(self.metadata, 'view')
            except AttributeError:
                setattr(self.metadata, 'view', [])
            list = getattr(self.metadata, 'view')
            list.append(child)
            #write the metadata to './metadata.xml'
            f = open('metadata.xml', 'wb')
            f.write(self.metadata.convertXML())
            f.close()
            


def main():
    print 'app starts'
    cv = cloudview() 
    cv.init()

if __name__ == "__main__":
    main()
