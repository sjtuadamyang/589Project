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
            f = open('./viewmeta.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            print self.metadata.folder[0].file[0]['name']
        except IOError:
            print 'no file named viewmeta.xml'

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
            self.metadata = boxdotnet.XMLNode()
            self.metadata.view[0][timestamp] = "0"

def main():
    print 'app starts'
    cv = cloudview() 
    cv.init

if __name__ == "__main__":
    main()
