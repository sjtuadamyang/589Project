#!/usr/bin/python
from threading import Thread, Lock, Event
from time import sleep

import boxdotnet
import time
import gdr_yyt
import os.path
import os
import sys
import logging
import random
import logging


logging.basicConfig(filename='.log', level=logging.DEBUG)

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
    #client_box = boxdotnet.BoxDotNet()
    #client_gdr = gdr_yyt.GOOGLE_VIEW()
    metadata = ''
    config = []#[type, Token_fn]
    client = []
    ser_metadata = ''
    local_file = []
    server_file = []
    cv_location = ''
    cv_current_dir = ''
    initialized = False
    folderRoot = folderNode('/')
    curFolderNode = folderRoot
    mutex = Lock()
    wakeup = Event()
    recovering_mode = '(normal mode)'
    configured_clients = 0
    authenticated_clients = 0

    def delete_all(self):
      #self.client_gdr.deleteall()
      #self.client_box.deleteall()
      for x in self.client:
          x.deleteall()

    def sync_thread_worker(self):
        while 1:
            if(self.wakeup.wait(5)):
                break
            self.wakeup.clear()
            self.mutex.acquire()
            logging.debug("synchronizing")
            self.sync()
            self.mutex.release()
            logging.debug("sync done")

    def run(self, testcase):
      if not self.initialized:
          print 'Initialization failed, exiting Cloudview'
          return
      self.sync()
      print 'New version'
      f = None
      if testcase:
        print testcase
        f =open(testcase[0], 'r+')
      self.sync_thread.start() 
      while (1):
        tmp_string = 'Cloudview'+self.recovering_mode+':'+self.cv_current_dir+'$' 
        if not testcase:
            command0 = raw_input(tmp_string)
        else:
            command0 = f.readline() 
        print 'Current Command: '+command0
        command = command0.split()
        try:
            if command == []:
                continue
            #if command[0] == 'sync':
            #    self.sync()
            #    continue
            if command[0] == 'ls':
                self.ls()
                continue
            if command[0] == 'add':
                if len(command) < 3:
                    print 'Current have ', len(self.config), ' accounts'
                    raise CVError("add <file path> <account index>")
                    continue
                self.mutex.acquire()
                self.add(command[1], command[2])
                self.mutex.release()
                continue
            if command[0] == 'delete':
                self.mutex.acquire()
                self.delete(command[1])
                self.mutex.release()
                continue
            if command[0]== 'deleteall':
                self.delete_all()
                continue
            if command[0] ==  'mkdir':
                self.mutex.acquire()
                self.mkdir(command[1])
                self.mutex.release()
                continue
            if command[0] == 'cd':
                self.cd(command[1])
                continue
            if command[0] == 'exit':
                print 'Existing CloudView'
                self.wakeup.set()
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
                self.wakeup.set()
                return
        os.system(command0)
        #self.wakeup.set()

    def __init__(self):
        self.sync_thread = Thread(target=self.sync_thread_worker)
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
        self.cv_location = os.getcwd()
        self.cv_current_dir = '/'

        try:
            config = open('./.config', 'rb')
            tmp = 0
            account_num = 0
            account = [0, 0] #['box'/'gdr', filename]
            tmp_words = config.read()
            for x in tmp_words.split():
                account[tmp] = x
                print 'x=', x
                tmp = tmp +1
                if tmp == 2:
                    tmp = 0
                    account_num  = account_num+1
                    self.config.append([account[0], account[1]])
                    print self.config
            self.configured_clients = len(self.config)
        except IOError:
            print 'no file named .config'
        self.init()

    def sync(self):
        s_ts = self.__retrieve_ser_metadata()
        self.server_file = self.__get_filelist(self.ser_metadata) 
        i = 0
        j = 0
        l_ts = int(self.metadata.view[0]['ts'])
        logging.debug("sync func info, l_ts is %d, s_ts is %d", l_ts, s_ts)
        if l_ts == s_ts:
            return
        while (i < len(self.local_file) and j < len(self.server_file)):
            local_entry = self.local_file[i]
            server_entry = self.server_file[j]
            if local_entry['title'] == '.av':
                i=i+1
                continue
            if  server_entry['title'] == '.av':
                if s_ts > l_ts:
                    self.folderRoot.add_child_path(os.path.dirname(server_entry['fullpath'])+'/')
                    #print self.cv_location
                    os.system('mkdir '+self.cv_location+os.path.dirname(server_entry['fullpath']))
                j=j+1
                continue
            x = self.client[int(local_entry.primary[0]['type'])]
            y = self.client[int(server_entry.primary[0]['type'])]
            x1 = self.client[int(local_entry.backup[0]['type'])]
            y1 = self.client[int(server_entry.backup[0]['type'])]
            x1_type = self.config[int(local_entry.backup[0]['type'])][0]
            y1_type = self.config[int(server_entry.backup[0]['type'])][0]
            if local_entry['id'] == server_entry['id']:
                if int(local_entry['ts'])>int(server_entry['ts']) or local_entry.primary[0]['status']=='1' or local_entry.backup[0]['status']=='1':
                    #upload to server and check box_id
                    if x.authenticated == True:
                        x.replace(local_entry.primary[0]['file_id'], cv_location+local_entry['fullpath'])
                        local_entry.primary[0]['status']='0'
                    else:
                        local_entry.primary[0]['status']='1'
                    if x1.authenticated == True:
                        x1.replace(local_entry.backup[0]['file_id'], cv_location+local_entry['fullpath'])
                        local_entry.backup[0]['status']='0'
                    else:
                        local_entry.backup[0]['status']='1'
                    '''
                    if local_entry.primary[0]['type']=='box':
                        self.client_box.replace(local_entry.primary[0]['file_id'], cv_location+local_entry['fullpath'])
                    if local_entry.primary[0]['type']=='gdr':
                        self.client_gdr.replace(local_entry.primary[0]['file_id'], cv_location+local_entry['fullpath'])
                    '''
                if int(local_entry['ts'])<int(server_entry['ts']):
                    #download from server and add path to current path tree
                    self.folderRoot.add_child_path(os.path.dirname(server_entry['fullpath'])+'/')
                    #print "download from "+x.type
                    succeed = False
                    if x.type == 'box':
                        if x.authenticated == True:
                             x.download(server_entry.primary[0]['file_id'], cv_location+server_entry['fullpath'])
                             succeed = True
                    if x.type == 'gdr':
                        if x.authenticated == True:
                             x.download(server_entry.primary[0]['download_url'], cv_location+server_entry['fullpath'])
                             succeed  = True
                    if succeed == False:
                        if x1.type == 'box':
                            if x1.authenticated == True:
                                x1.download(server_entry.primary[0]['file_id'], cv_location+server_entry['fullpath'])
                                succeed = True
                        if x1.type == 'gdr':
                            if x1.authenticated == True:
                                x1.download(server_entry.primary[0]['download_url'], cv_location+server_entry['fullpath'])
                                succeed  = True
                    if succeed == False:
                        print 'Too many accouts not available, data corrupted...'
                         
                    '''
                    if local_entry.primary[0]['type']=='box':
                        self.client_box.download(server_entry.primary[0]['file_id'], cv_location+server_entry['fullpath'])
                    if local_entry.primary[0]['type']=='gdr':
                        self.client_gdr.download(server_entry.primary[0]['download_url'], cv_location+server_entry['fullpath'])
                    '''
                i=i+1
                j=j+1
                continue
            if local_entry['id'] > server_entry['id']:
                if l_ts>s_ts:
                    #delete server files
                    if x.authenticated == True:
                        x.delete(server_entry.primary[0]['file_id'])
                    if x1.authenticated == True:
                        x1.delete(server_entry.backup[0]['file_id'])
                    '''
                    if server_entry.primary[0]['type']=='box':
                        self.client_box.delete(server_entry.primary[0]['file_id'])
                    if server_entry.primary[0]['type']=='gdr':
                        self.client_gdr.delete(server_entry.primary[0]['file_id'])
                    '''
                else:
                    #not possible, we need to raise an exception
                    raise CVError("l_ts < s_ts happended, something wrong with our logic")
                j=j+1
                continue
            if local_entry['id'] < server_entry['id']:
                #delete local files
                fullpath = self.cv_location + local_entry['fullpath']
                os.system('rm '+fullpath)
                i=i+1
                continue
        
        if i<len(self.local_file):
            for index in range(i, len(self.local_file)):
                local_entry = self.local_file[index]
                if local_entry['title'] == '.av':
                    continue
                x = self.client[int(local_entry.primary[0]['type'])]
                 
                x1 = self.client[int(local_entry.backup[0]['type'])]
                x1_type = self.config[int(local_entry.backup[0]['type'])][0]
                if l_ts<s_ts:
                    #delete all remain files
                    fullpath = self.cv_location + local_entry['fullpath']
                    os.system('rm '+fullpath)
                elif l_ts>s_ts or local_entry.primary[0]['status'] =='1'or local_entry.backup[0]['status']=='1':
                    #upload all remain files
                    if x.type=='box':
                        if x.authenticated == True:
                            file_id = x.upload(self.cv_location + local_entry['fullpath'], local_entry['id'])
                            local_entry.primary[0]['file_id'] = str(file_id)
                            local_entry.primary[0]['status'] = '0'
                        else:
                            local_entry.primary[0]['status'] = '1'
                    if x.type=='gdr':
                        if x.authenticated == True:
                            file_id, download_url = x.upload(self.cv_location + local_entry['fullpath'])
                            local_entry.primary[0]['file_id'] = str(file_id)
                            #print download_url
                            local_entry.primary[0]['download_url'] = download_url
                            local_entry.primary[0]['status'] = '0'
                        else:
                            local_entry.primary[0]['status'] = '1'
                    #print x1_type
                    if x1_type=='box':
                        if x1.authenticated == True:
                            file_id = x1.upload(self.cv_location + local_entry['fullpath'], local_entry['id'])
                            local_entry.backup[0]['file_id'] = str(file_id)
                            local_entry.backup[0]['status'] = '0'
                        else:
                            local_entry.backup[0]['status'] = '1'
                    if x1_type=='gdr':
                        if x1.authenticated == True:
                            file_id, download_url = x1.upload(self.cv_location + local_entry['fullpath'])
                            local_entry.backup[0]['file_id'] = str(file_id)
                            #print download_url
                            local_entry.backup[0]['download_url'] = download_url
                            local_entry.backup[0]['status'] = '0'
                        else:
                            local_entry.backup[0]['status'] = '1'


        if j<len(self.server_file):
            for index in range(j, len(self.server_file)):
                server_entry = self.server_file[index]
                logging.debug("in the j < len loop, l_ts is %d, s_ts is %d", l_ts, s_ts)
                if server_entry['title'] == '.av':
                    if l_ts > s_ts:
                        continue
                    self.folderRoot.add_child_path(os.path.dirname(server_entry['fullpath'])+'/')
                    #print self.cv_location
                    os.system('mkdir '+self.cv_location+os.path.dirname(server_entry['fullpath']))
                    continue
                y = self.client[int(server_entry.primary[0]['type'])]
                y1 = self.client[int(server_entry.backup[0]['type'])]
                y1_type = self.config[int(server_entry.backup[0]['type'])][0]
                if l_ts<s_ts:
                    #download all remaining files and update folder tree
                    self.folderRoot.add_child_path(os.path.dirname(server_entry['fullpath'])+'/')
                    #print y.type
                    succeed = False
                    if y.type=='box':
                        #print "box download " 
                        if y.authenticated == True:
                            y.download(server_entry.primary[0]['file_id'], self.cv_location+server_entry['fullpath'])
                            succeed = True
                    if y.type=='gdr':
                        if y.authenticated == True:
                            y.download(server_entry.primary[0]['download_url'], self.cv_location+server_entry['fullpath'])
                            succeed = True
                    if succeed  == True:
                        continue
                    if y1_type=='box':
                        #print "box download " 
                        if y1.authenticated == True:
                            y1.download(server_entry.backup[0]['file_id'], self.cv_location+server_entry['fullpath'])
                            succeed = True
                    if y1_type=='gdr':
                        if y1.authenticated == True:
                            y1.download(server_entry.backup[0]['download_url'], self.cv_location+server_entry['fullpath'])
                            succeed = True
                    if succeed == False:
                        print 'Too many accounts down, data corrupted'
                elif l_ts>s_ts:
                    #delete all remaining files
                    
                    if y.authenticated == True:
                        y.delete(server_entry.primary[0]['file_id'])
                    if y1.authenticated == True:
                        y1.delete(server_entry.backup[0]['file_id'])
                    '''
                    if server_entry.primary[0]['type']=='box':
                        self.client_box.delete(server_entry.primary[0]['file_id'])
                    if server_entry.primary[0]['type']=='gdr':
                        self.client_gdr.delete(server_entry.primary[0]['file_id'])
                    '''
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
            for x in self.client:
                if x.authenticated == False:
                    continue
                x.setmetadata('.metadata.xml')


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
        max_ts = -1
        for x in self.client:
            if x.authenticated == False:
                continue
            sermeta = x.getmetadata()
            tmp_ts = 0 if (sermeta==None) else int(sermeta.view[0]['ts'])
            if (tmp_ts > max_ts):
              max_ts = tmp_ts
              self.ser_metadata = sermeta
        return max_ts
        '''
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
        '''


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
        prime['status']='0'
        setattr(file, 'primary', [])
        file.primary.append(prime)
        backup = boxdotnet.XMLNode()
        backup.elementName = 'backup'
        tmp = int(primary)
        while (tmp == int(primary)):
            tmp = random.randint(0, len(self.client)-1)
        backup['type']=str(tmp)
        backup['file_id']=''
        backup['download_url']=''
        backup['status']='0'
        setattr(file, 'backup', [])
        file.backup.append(backup)
        self.metadata.view[0]['cur_id']=str(int(self.metadata.view[0]['cur_id'])+1)
        self.metadata.view[0]['ts']=file['ts']
        self.metadata.view[0].file.append(file)

    def mkdir(self, dirname):
        fspath = self.cv_location+self.cv_current_dir+dirname
        title = os.path.basename(dirname)
        if os.path.exists(fspath):
            raise CVError("path already exist")
        
        if not title==dirname:
            raise CVError("filename can not be a path name")
        command = 'mkdir '+fspath
        print 'fspath is = '+fspath
        os.system(command)
        self.folderRoot.add_child_path(self.cv_current_dir+dirname+'/')
        self.cd(dirname)
        #print self.cv_location+'.av'
        #os.system('touch '+self.cv_location+self.cv_current_dir+'.av')
        #self.add(self.cv_location+self.cv_current_dir+'.av', 'box')
        #add a .av file to current metadata list
        try:
            getattr(self.metadata.view[0], 'file')
        except AttributeError:
            setattr(self.metadata.view[0], 'file', [])

        file = boxdotnet.XMLNode() 
        file.elementName = 'file'
        file['title']='.av'
        file['fullpath']=self.cv_current_dir+'.av'
        self.metadata.view[0].file.append(file)
        self.metadata.view[0]['ts']=str(int(time.time()))
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
        f = open ('.config', 'wb')
        if not f:
            raise CVError('.config file not exist')
        for x in self.config:
            print x
            f.write(x[0]+' '+str(x[1])+' ')
        f.close

    def init(self):

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
        if self.config == []:
            # needs to login first
            print 'Login in using box account or google drive'
            num_accounts = 0

            print 'how many account do you have'
            self.configured_clients = int(raw_input())

            for i in range(0, self.configured_clients):
                input = '' 
                while input != '1' and input != '2':
                    print 'Choose account'+str(i)+' type: 1) Box 2) Google Drive'
                    input = raw_input();

                if input== '1':
                    tmp = ['box', '.Token'+str(i)]
                    self.client.append(boxdotnet.BoxDotNet())
                    self.config.append(['box', i])
                elif input == '2':
                    tmp = ['gdr', '.Token'+str(i)]
                    self.client.append(gdr_yyt.GOOGLE_VIEW())
                    self.config.append(['gdr', i])
                    continue

            """
            Continue = True
            while (Continue):
                print 'Choose account type: 1) Box 2) Google Drive'
                i = raw_input();
                if i== '1':
                    tmp = ['box', '.Token'+str(num_accounts)]
                    self.client.append(boxdotnet.BoxDotNet())
                    self.config.append(['box', num_accounts])
                elif i == '2':
                    tmp = ['gdr', '.Token'+str(num_accounts)]
                    self.client.append(gdr_yyt.GOOGLE_VIEW())
                    self.config.append(['gdr', num_accounts])
                else:
                    print 'Account not supported'
                    continue
                num_accounts = num_accounts+1
                
                print 'Continue adding new accounts? y for Yes'
                i = raw_input()
                if i != 'y':
                    Continue = False
            """
            print 'default cloud location for file addition'

        """all the client do authentication"""
        file_idex = 0
        print 'length of client is '+str(len(self.client))
        print self.config
        if len(self.client)==0:
            for x in self.config:
                if x[0] == 'box':
                    tmp = ['box', x[1]]
                    self.client.append(boxdotnet.BoxDotNet())
                elif x[0] == 'gdr':
                    tmp = ['gdr', x[1]]
                    self.client.append(gdr_yyt.GOOGLE_VIEW())
        print self.config, '<------------Here'
        print 'length of client is '+str(len(self.client))
        for x in self.client:
            print 'x in client x.authentication is '+str(x.authenticated)
            if not x.authenticated:
                print 'call authenticate with '+'.Token'+str(file_idex)
                x.authenticate('.Token'+str(file_idex))
            file_idex = file_idex +1
        for x in self.client:
            if x.authenticated:
                self.authenticated_clients += 1
            
        print 'number of configured clients '+str(self.configured_clients)
        print 'number of authenticated clients '+str(self.authenticated_clients)
        if self.authenticated_clients <= self.configured_clients - 2:
            self.initialized = False
            return 
        if self.authenticated_clients == self.configured_clients - 1:
            self.recovering_mode = '(recovering mode)'
        self.initialized = True

    def featureTest(self):
        pass

def main(argv):
    print 'app starts'
    cv = cloudview() 
    cv.run(argv)
    cv.sync()
    cv.write_meta()

if __name__ == "__main__":
    main(sys.argv[1:])
