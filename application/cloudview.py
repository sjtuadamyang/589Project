#!/usr/bin/python

import boxdotnet
import time
import gdr_yyt
import os.path
import os
import sys
import logging

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
        self.childNodes = []
    def get_child(self):
        ret = ''
        for item in self.childNodes:
            ret += item.name+' '
        return ret

    def print_tree(self):
        print "current level "+self.name
        print 'length of childs: '+str(len(self.childNodes))
        print ''
        for item in self.childNodes:
            print "we get here"
            item.print_tree()      

    def add_child(self, name):
        child = folderNode(name)
        child.parent = self
        self.childNodes.append(child)
        return child

    def add_child_path(self, path):
        components = path.split(os.sep)
        curNode = self
        index = 1
        while index < len(components)-1:
            #print "checking components "+components[index]
            find = False 
            for item in curNode.childNodes:
                if item.name == components[index]:
                    curNode = item
                    find = True
            if find == False:
                #print "test: add a child "+components[index]+" at "+curNode.name     
                newNode = curNode.add_child(components[index])
                curNode = newNode
            index += 1
        #print "test: after adding node we curNode is "+curNode.name

    def cd_to_path(self, dir):
        if dir == '..' or dir == '../':
            try:
                getattr(self, 'parent')
            except AttributeError:
                raise CVError("no parent for current dir")
            return self.parent
        for item in self.childNodes:
            if item.name == dir:
                return item
        raise CVError("no dir found")

class cloudview:
    client_box = boxdotnet.BoxDotNet()
    client_gdr = gdr_yyt.GOOGLE_VIEW()
    metadata = ''
    ser_metadata = ''
    local_file = []
    server_file = []
    cv_location = ''
    cv_current_dir = ''
    initialized = False
    folderRoot = folderNode('/')
    curFolderNode = folderRoot

    def delete_all(self):
      self.client_gdr.deleteall()
      self.client_box.deleteall()


    def run(self, testcase):
      f = None
      if testcase:
        print testcase
        f =open(testcase[0], 'r+')
      while (1):
        tmp_string = 'Cloudview:'+self.cv_current_dir+'$' 
        if not testcase:
            command0 = raw_input(tmp_string)
        else:
            command0 = f.readline() 
        print 'Current Command: '+command0
        command = command0.split()
        try:
            if command[0] == 'sync':
                self.sync()
                continue
            if command[0] == 'ls':
                self.ls()
                continue
            if command[0] == 'add':
                if len(command) < 3:
                    raise CVError("add <file path> <primary type>")
                    continue
                self.add(command[1], command[2])
                continue
            if command[0] == 'delete':
                self.delete(command[1])
                continue
            if command[0]== 'deleteall':
                self.delete_all()
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
        except CVError as e:
            print str(e)
            rinput = None
            while (not rinput == 'Y') and (not rinput == 'N'):
                print "still continue test?Y:N"
                rinput = raw_input() 
            if rinput == 'Y':
                continue
            else:
                print "Not continuing, existing CloudView"
                return
        os.system(command0)

    def __init__(self):
        try:
            f = open('./.metadata.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            try:
                getattr(self.metadata.view[0], 'file')
            except AttributeError:
                setattr(self.metadata.view[0], 'file', [])
            self.local_file = self.__get_filelist(self.metadata)
            for file in self.local_file:
                print os.path.dirname(file['fullpath'])
                self.folderRoot.add_child_path(os.path.dirname(file['fullpath']+'/'))
            print "local view is at stamp: " + str(self.metadata.view[0]['ts'])
        except IOError:
            print 'no file named .metadata.xml'
        except Exception:
            print '.metadata.xml is garbage'
        self.cv_location = os.path.dirname(os.path.realpath(__file__))
        self.cv_current_dir = '/'

    def sync(self):
        s_ts = self.__retrieve_ser_metadata()
        self.server_file = self.__get_filelist(self.ser_metadata) 
        #print len(self.local_file)
        #print len(self.server_file)
        i = 0
        j = 0
        l_ts = int(self.metadata.view[0]['ts'])
        #print l_ts, s_ts
        while (i < len(self.local_file) and j < len(self.server_file)):
            local_entry = self.local_file[i]
            server_entry = self.server_file[j]
            if local_entry['id'] == server_entry['id']:
                if int(local_entry['ts'])>int(server_entry['ts']):
                    #upload to server and check box_id
                    if local_entry.primary[0]['type']=='box':
                        self.client_box.replace(local_entry.primary[0]['file_id'], cv_location+local_entry['fullpath'])
                    if local_entry.primary[0]['type']=='gdr':
                        self.client_gdr.replace(local_entry.primary[0]['file_id'], cv_location+local_entry['fullpath'])
                if int(local_entry['ts'])<int(server_entry['ts']):
                    #download from server and add path to current path tree
                    self.folderRoot.add_child_path(os.path.dirname(server_entry['fullpath'])+'/')
                    if local_entry.primary[0]['type']=='box':
                        self.client_box.download(server_entry.primary[0]['file_id'], cv_location+server_entry['fullpath'])
                    if local_entry.primary[0]['type']=='gdr':
                        self.client_gdr.download(server_entry.primary[0]['download_url'], cv_location+server_entry['fullpath'])
                    
                i=i+1
                j=j+1
                continue
            if local_entry['id'] > server_entry['id']:
                """:)"""
                if l_ts>s_ts:
                    #delete server files
                    if server_entry.primary[0]['type']=='box':
                        self.client_box.delete(server_entry.primary[0]['file_id'])
                    if server_entry.primary[0]['type']=='gdr':
                        self.client_gdr.delete(server_entry.primary[0]['file_id'])
                else:
                    #not possible, we need to raise an exception
                    raise CVError("l_ts < s_ts happended, something wrong with our logic")
                j=j+1
                continue
            if local_entry['id'] < server_entry['id']:
                """:)"""
                #delete local files
                fullpath = self.cv_location + local_entry['fullpath']
                os.system('rm '+fullpath)
                i=i+1
                continue
        
        if i<len(self.local_file):
            for index in range(i, len(self.local_file)):
                local_entry = self.local_file[index]
                if l_ts<s_ts:
                    #delete all remain files
                    fullpath = self.cv_location + local_entry['fullpath']
                    os.system('rm '+fullpath)
                else:
                    #upload all remain files
                    if local_entry['title'] == '.av':
                        continue
                    if local_entry.primary[0]['type']=='box':
                        file_id = self.client_box.upload(self.cv_location + local_entry['fullpath'], local_entry['id'])
                        local_entry.primary[0]['file_id'] = str(file_id)
                    if local_entry.primary[0]['type']=='gdr':
                        file_id, download_url = self.client_gdr.upload(self.cv_location + local_entry['fullpath'])
                        local_entry.primary[0]['file_id'] = str(file_id)
                        #print download_url
                        local_entry.primary[0]['download_url'] = download_url


        if j<len(self.server_file):
            for index in range(j, len(self.server_file)):
                server_entry = self.server_file[index]
                if l_ts<s_ts:
                    #download all remaining files and update folder tree
                    self.folderRoot.add_child_path(os.path.dirname(server_entry['fullpath'])+'/')
                    if server_entry['title'] == '.av':
                        continue
                    if server_entry.primary[0]['type']=='box':
                        self.client_box.download(server_entry.primary[0]['file_id'], self.cv_location+server_entry['fullpath'])
                    if server_entry.primary[0]['type']=='gdr':
                        self.client_gdr.download(server_entry.primary[0]['download_url'], self.cv_location+server_entry['fullpath'])
                else:
                    #delete all remaining files
                    if server_entry.primary[0]['type']=='box':
                        self.client_box.delete(server_entry.primary[0]['file_id'])
                    if server_entry.primary[0]['type']=='gdr':
                        self.client_gdr.delete(server_entry.primary[0]['file_id'])
        #sync metalist
        if l_ts<s_ts:
            self.metadata = self.ser_metadata
            #write down to metadata.xml
            f = open('.metadata.xml', 'wb')
            f.write(self.metadata.convertXML())
            f.close()
        if l_ts>s_ts:
            #write down to metadata.xml
            f = open('.metadata.xml', 'wb')
            f.write(self.metadata.convertXML())
            f.close()
            #upload self.metalist to all servers
            self.client_gdr.setmetadata('.metadata.xml')
            self.client_box.setmetadata('.metadata.xml')


    def __get_filelist(self, metadata):
        if isinstance(metadata, boxdotnet.XMLNode):
            try:
                getattr(metadata.view[0], 'file')
            except AttributeError:
                setattr(metadata.view[0], 'file', [])
            return metadata.view[0].file
        return []

    def __retrieve_ser_metadata(self):
        """get the most updated server metadata"""
        boxmeta = self.client_box.getmetadata()
        box_ts = 0 if (boxmeta==None) else int(boxmeta.view[0]['ts'])
        gdrmeta = self.client_gdr.getmetadata()
        gdr_ts = 0 if (gdrmeta==None) else int(gdrmeta.view[0]['ts'])
        if box_ts > gdr_ts:
            self.ser_metadata = boxmeta
            return box_ts
        else:
            self.ser_metadata = gdrmeta
            return gdr_ts

    def ls(self):
        """not implemented yet"""
        #print "current tree is : "
        #self.folderRoot.print_tree()
        list = '' 
        if not self.initialized:
            raise CVError("application not initialized")
        for file in self.metadata.view[0].file:
            if file['fullpath'] == self.cv_current_dir + file['title']:
                list += file['title']+' '

        #print "curFolderNode name is"+str(self.curFolderNode.name)
       
        list += self.curFolderNode.get_child()
        print list

    def add(self, filename, primary):
        """not implemented yet"""
        #filename need to be absolute address
        title = os.path.basename(filename)
        #transfer title into abs address
        fspath = self.cv_location+self.cv_current_dir +title
        command = 'cp '+filename+' '+fspath
        if not os.path.isfile(os.path.expanduser(filename)):
            raise CVError("file not exist")
        #print command
        os.system(command)
        try:
            getattr(self.metadata.view[0], 'file')
        except AttributeError:
            setattr(self.metadata.view[0], 'file', [])
        for file in self.metadata.view[0].file:
            if file['fullpath'] == self.cv_current_dir+title:
                if file.primary[0]['type']!=primary:
                    raise CVError("File already exist on another cloud")
                file['ts']=str(int(time.time()))
                self.metadata.view[0]['ts']=file['ts']
                #print self.metadata.convertXML()
                return
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
        #print self.metadata.convertXML()

    def mkdir(self, dirname):
        fspath = self.cv_location+self.cv_current_dir+dirname
        title = os.path.basename(dirname)
        if os.path.exists(fspath):
            raise CVError("path already exist")
        
        if not title==dirname:
            raise CVError("filename can not be a path name")
        command = 'mkdir '+fspath
        os.system(command)
        self.folderRoot.add_child_path(self.cv_current_dir+dirname+'/')
        self.cd(dirname)
        #print self.cv_location+'.av'
        #os.system('touch '+self.cv_location+self.cv_current_dir+'.av')
        #self.add(self.cv_location+self.cv_current_dir+'.av', 'box')
        self.cd('../')

    def delete(self, filename):
        """not implemented yet"""
        title = os.path.basename(filename)
        if not title==filename:
            raise CVError("filename can not be a path name")
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
        self.metadata.view[0]['ts']=str(int(time.time()))
        #print self.metadata.convertXML()
        
    def cd(self, dir):
        if not os.path.isdir(self.cv_location+self.cv_current_dir+dir):
            raise CVError("dir not exist")
        self.curFolderNode = self.curFolderNode.cd_to_path(dir)
        self.cv_current_dir = self.cv_current_dir + dir + '/'
        self.cv_current_dir = '/'+os.path.relpath(os.path.abspath(self.cv_location+self.cv_current_dir), self.cv_location)+'/'
        if self.cv_current_dir == '/./':
            self.cv_current_dir='/'

    def write_meta(self):
        f = open('.metadata.xml', 'wb')
        if not f:
            raise CVError("metadata.xml not exist")
        f.write(self.metadata.convertXML())
        f.close

    def init(self):
        """all the client do authentication"""
        if not self.client_box.authenticated:
            self.client_box.authenticate()
        if not self.client_gdr.Drive_Service:
            self.client_gdr.authent()

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
            child['cur_id']='1'
            setattr(child, 'file', [])
            #id 0 is reserved for metadata.xml
            try:
                list = getattr(self.metadata, 'view')
            except AttributeError:
                setattr(self.metadata, 'view', [])
            list = getattr(self.metadata, 'view')
            list.append(child)
            self.local_file = self.__get_filelist(self.metadata)
            #write the metadata to './metadata.xml'
            #it seems we do not need to write at this time
            f = open('.metadata.xml', 'wb')
            f.write(self.metadata.convertXML())
            f.close()
        self.initialized = True

    def featureTest(self):
        pass

def main(argv):
    print 'app starts'
    cv = cloudview() 
    cv.init()
    cv.sync()
    cv.run(argv)
    cv.write_meta()

if __name__ == "__main__":
    main(sys.argv[1:])
