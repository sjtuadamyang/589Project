#!/usr/bin/python

import boxdotnet
import os.path

class cloudview:
    client = boxdotnet.BoxDotNet()
    app_id = '9cluykmx5i2filqz202p1t5frptgtjwn'
    needlogin = False
    token = ''
    metadata = ''
    def __init__(self):
        #start login process
        try:
            f = open('Token', 'rb')
            self.token = f.read();
            if self.token == '': 
                print 'we got nothing and we need to login'
                self.needlogin = True
            f.close()
        except IOError:
            print 'no token file been established'
            self.needlogin = True

        try:
            f = open('./metadata.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            print self.metadata.view[0]['ts']
        except IOError:
            print 'no file named metadata.xml'

    def sync(self):
        """not implemented yet"""

    def init(self):
        """not implemented yet"""
        if self.needlogin:
            rsp = self.client.login(self.app_id)
            self.token = rsp.auth_token[0].elementText
            f = open('Token', 'wb')
            f.write(self.token)
            f.close()

        if self.metadata == '':
            #init a empty metadata file
            self.metadata = boxdotnet.XMLNode()
            self.metadata.elementName='metadata'
            #add a view with ts of 0
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
