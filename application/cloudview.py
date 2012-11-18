#!/usr/bin/python

import boxdotnet
import time
import gdr_yyt
import os.path
import os

class CVError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class folderNode:
    childNodes = []
    name = ''
    def __init__(self, name):
        self.name = name 
    def get_child(self):
        ret = ''
        for item in self.childNodes:
            ret += ' '+self.childNodes.name 
        return ret
    def add_child(self, name):
        child = folderNode(name)
        childNodes.append(child)
        return child
    def add_child_path(self, path):
        components = path.split(os.sep)
        curNode = self
        index = 1
        while index < len(components)-1:
            try:
                find = curNode.childNodes.index(components[index])
                curNode = curNode.childNodes[find]
            except ValueError:
                newNode = curNode.add_child(components[index])
                curNode = newNode 
    def cd_to_path(self, dir):
        for item in self.childNodes:
            if item.name == dir:
                return item

class cloudview:
    client_box = boxdotnet.BoxDotNet()
    client_gd = gdr_yyt.GOOGLE_VIEW()
    metadata = ''
    ser_metadata = ''
    local_file = []
    server_file = []
    cv_location = ''
    cv_current_dir = ''
    initialized = False
    folderRoot = folderNode('/')
    curFolderNode = folderRoot

    def run(self):
      while (1):
        tmp_string = 'Cloudview:'+self.cv_current_dir+'$' 
        command = raw_input(tmp_string)
        command = command.split()
        if command[0] == 'sync':
            self.sync()
            continue
        if command[0] == 'ls':
            self.ls()
            continue
        if command[0] == 'add':
            self.add(command[1], command[2])
            continue
        if command[0] == 'delete':
            self.delete(command[1])
            continue
        if command[0] ==  'mkdir':
            self.mkdir(command[1])
            continue
        if command[0] == 'cd':
            self.cd(command[1])
            continue
        if command[0] == 'exit':
            print 'Existing CloudView'
            return
        print 'Command Not Exists'
        print 'Commands:\nsync:\t\t\tsyncnize between server and local\nls:\t\t\tlist all the files\nadd filename drive:\tadd new file to the current directory\ndelete filename:\tdelete file under current directory\nmkdir dir:\t\tmake new directory under current directory\ncd dir:\t\t\tgoto certain directory\nexit:\t\t\texit CloudView'

    def __init__(self):
        try:
            f = open('./metadata.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            self.local_file = self.__get_filelist(self.metadata)
            for file in self.local_file:
                folderTree.add_child_path(file['fullpath'])
            print "local view is at stamp: " + str(self.metadata.view[0]['ts'])
        except IOError:
            print 'no file named metadata.xml'
        self.cv_location = os.path.dirname(os.path.realpath(__file__))
        self.cv_current_dir = '/'

    def sync(self):
        self.__retrieve_ser_metadata()
        self.server_file = self.__get_filelist(self.ser_metadata) 
        print len(self.local_file)
        print len(self.server_file)
        i = 0
        j = 0
        while i < len(local_file) and j < len(server_file)
            if local_file[i]['id'] 
    
    def __get_filelist(self, metadata):
        if isinstance(metadata, boxdotnet.XMLNode):
            try:
                getattr(metadata.view[0], 'file')
            except AttributeError:
                return []
            return metadata.view[0].file
        return []

    def __retrieve_ser_metadata(self):
        """get the most updated server metadata"""
        boxmeta = self.client_box.getmetadata()
        box_ts = -1 if (boxmeta==None) else int(boxmeta.view[0]['ts'])
        gdrmeta = self.client_gd.retrieve_metadata()
        gdr_ts = -1 if (gdrmeta==None) else int(gdrmeta.view[0]['ts'])
        self.ser_metadata = boxmeta if (box_ts>gdr_ts) else gdrmeta 

    def ls(self):
        """not implemented yet"""
        list = '' 
        if not self.initialized:
            raise Exception(CVError, "application not initialized")
        for file in self.metadata.view[0].file:
            if file['fullpath'] == self.cv_current_dir + file['title']:
                list += ' '+file['title']
        childlist = self.curFolderNode.get_child()
        for dir in self.childlist:
            list += ' '+dir.name

    def add(self, filename, primary):
        """not implemented yet"""
        #filename need to be absolute address
        title = os.path.basename(filename)
        #transfer title into abs address
        fspath = self.cv_location+self.cv_current_dir +title
        command = 'cp '+filename+' '+fspath
        if not os.path.isfile(os.path.expanduser(filename)):
            raise Exception(CVError, "file not exist")
        #print command
        os.system(command)
        try:
            getattr(self.metadata.view[0], 'file')
        except AttributeError:
            setattr(self.metadata.view[0], 'file', [])
        for file in self.metadata.view[0].file:
            if file['fullpath'] == self.cv_current_dir+title:
                file['ts']=str(int(time.time()))
                print self.metadata.convertXML()
        #add file information to metalist
        file = boxdotnet.XMLNode() 
        file.elementName = 'file'
        file['title']=title
        file['id']=self.metadata.view[0]['cur_id']
        file['fullpath']=self.cv_current_dir+title
        file['ts']=str(int(time.time()))

        prime = boxdotnet.XMLNode()
        prime.elementName = 'primary'
        prime['type']=primary
        prime['file_id']=''
        prime['download_url']=''
        setattr(file, 'primary', [])
        file.primary.append(prime)
        self.metadata.view[0]['cur_id']=str(int(self.metadata.view[0]['cur_id'])+1)
        self.metadata.view[0]['ts']=file['ts']
        self.metadata.view[0].file.append(file)
        print self.metadata.convertXML()

    def mkdir(self, dirname):
        fspath = self.cv_location+self.cv_current_dir+dirname
        title = os.path.basename(dirname)
        if os.path.exists(fspath):
            raise Exception(CVError, "path already exist")
        
        if not title==dirname:
            raise Exception(CVError, "filename can not be a path name")
        command = 'mkdir '+fspath
        os.system(command)

    def delete(self, filename):
        """not implemented yet"""
        title = os.path.basename(filename)
        if not title==filename:
            raise Exception(CVError, "filename can not be a path name")
        #transfer filename into absolute address
        title = self.cv_location+self.cv_current_dir+title
        command = 'rm '+title
        os.system(command)
        #bug: if file does not exist
        #delete entry in metadatalist
        for file in self.metadata.view[0].file:
            if file['fullpath'] == self.cv_current_dir+filename:
                #delete
                self.metadata.view[0].file.remove(file)
        print self.metadata.convertXML()

    def cd(self, dir):
        if not os.path.isdir(self.cv_location+self.cv_current_dir+dir):
            raise Exception(CVError, "dir not exist")
        self.cv_current_dir = self.cv_current_dir + dir + '/'
        self.cv_current_dir = '/'+os.path.relpath(os.path.abspath(self.cv_location+self.cv_current_dir), self.cv_location)+'/'
        if self.cv_current_dir == '/./':
            self.cv_current_dir='/'

    def write_meta(self):
        f = open('metadata.xml', 'wb')
        if not f:
            raise Exception(CVError, "metadata.xml not exist")
        f.write(self.metadata.convertXML())
        f.close

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
    cv.run()

if __name__ == "__main__":
    main()
