#!/usr/bin/python

import boxdotnet
import time
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
        self.cv_location = os.path.dirname(os.path.realpath(__file__))
        self.cv_current_dir = '/'

    def sync(self):
        """create folder
            compare metadata lists, choose to upload or download according to the timestamp"""

    def ls(self):
        """not implemented yet"""
        list = '' 
        if not self.initialized:
            raise Exception(CVError, "application not initialized")
        for file in metadata.view[0].file:
            if file['fullpath'] == cv_current_dir + file['title']:
                list += '\n'+file[title]
        return list

    def add(self, filename, primary):
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
        file['ts']=str(int(time.time()))
        metadata['id']=str(int(metadata['id'])+1)
        metadata.view[0].file.append(file)

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
        for file in metadata.view[0].file:
            if file['fullpath'] == cv_current_dir+title:
                #delete
                metadata.view[0].file.remove(file)

    def cd(self, dir):
        if not os.path.isdir(self.cv_location+self.cv_current_dir+dir):
            raise Exception(CVError, "dir not exist")
        self.cv_current_dir = self.cv_current_dir + dir

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
                <view ts='0' cur_id='0'/>
            </metadata>
            """
            self.metadata = boxdotnet.XMLNode()
            self.metadata.elementName='metadata'
            child = boxdotnet.XMLNode()
            child.elementName = 'view'
            child['ts']='0'
            child['cur_id']='0'
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
        self.initialized = True

    def featureTest(self):
    
        """metaNode_1 = self.client_box.getmetadata()    
        self.client_gd.upload('metadata.xml', 'metadata.xml')
        metaNode_2 = self.client_gd.retrieve_metadata()    
        if not metaNode_2 == None:
            print 'gdr metadata'
            print metaNode_2.convertXML()"""

def main():
    print 'app starts'
    cv = cloudview() 
    cv.init()
    cv.featureTest()

if __name__ == "__main__":
    main()
