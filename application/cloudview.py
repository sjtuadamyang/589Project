#!/usr/bin/python

import boxdotnet
import gdr_yyt
import os.path

class cloudview:
    #client_gd.retrieve_metadata()
        #compare  metas
        #if self.metadata.view[0] == 0:
        #    self.metadata = client_gd.metadata
        #while loop starts
        """create folder"""
        """compare metadata lists, choose to upload or download according to the timestamp"""
              

    def init(self):
        """all the client do authentication"""
        if not self.client_box.authenticated:
            self.client_box.authenticate()
        #if not self.client_gd.Drive_Service:
        #    self.client_gd.authent()

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

    def featureTest(self):
        metaNode = self.client_box.getmetadata()    
        if not metaNode == None:
            print metaNode.convertXML()
        #self.client_box.upload("metadata.xml", "metadata.xml")

def main():
    print 'app starts'
    cv = cloudview() 
    cv.init()
    #cv.featureTest()

if __name__ == "__main__":
    main()
