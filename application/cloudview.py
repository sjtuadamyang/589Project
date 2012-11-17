#!/usr/bin/python

import boxdotnet
import gdr_yyt
import os.path
import os

class cloudview:
    client_box = boxdotnet.BoxDotNet()
    client_gd = gdr_yyt.GOOGLE_VIEW()
    metadata = ''
    cv_location = ''
    cv_current_dir = ''
    initialized = False

    def __init__(self):
        try:
            f = open('./metadata.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            print "local view is at stamp: " + str(self.metadata.view[0]['ts'])
        except IOError:
            print 'no file named metadata.xml'

    def sync(self):
        """create folder
            compare metadata lists, choose to upload or download according to the timestamp"""

    def ls(self):
        """not implemented yet"""

    def add(self, filename):
        """not implemented yet"""
        #filename need to be absolute address
        title = os.path.basename(filename)
        #transfer title into abs address
        title = cv_location+cv_current_dir +title
        command = 'cp '+filename+' '+title
        os.system(command)
        #add file information to metalist
        file['title']=title
        file['id']=metadata['id']
        metadata['id']=str(int(metadata['id'])+1)

    def delete(self, filename):
        """not implemented yet"""
        title = os.path.basename(filename)
        if not title==filename:
            print 'delete can only delete files under current directory'
        #transfer filename into absolute address
        title = cv_location+cv_current_dir+title
        command = 'rm '+title
        os.system(command)
        #delete entry in metadatalist

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

    def featureTest(self):
        metaNode_1 = self.client_box.getmetadata()    
        self.client_gd.upload('metadata.xml', 'metadata.xml')
        metaNode_2 = self.client_gd.retrieve_metadata()    
        if not metaNode_2 == None:
            print 'gdr metadata'
            print metaNode_2.convertXML()

def main():
    print 'app starts'
    cv = cloudview() 
    cv.init()
    cv.featureTest()

if __name__ == "__main__":
    main()
