#!/usr/bin/python

import boxdotnet
import gdr_yyt
import os.path

class cloudview:
    client_gd = gdr_yyt.GOOGLE_VIEW()
    client_box = boxdotnet.BoxDotNet()
    #app_id = '9cluykmx5i2filqz202p1t5frptgtjwn'
    #needlogin = False
    #token = ''
    metadata = ''
    def __init__(self):
        #start login process
        #try:
        #    f = open('Token', 'rb')
        #    self.token = f.read();
        #    if self.token == '': 
        #        print 'we got nothing and we need to login'
        #        self.needlogin = True
        #    f.close()
        #except IOError:
        #    print 'no token file been established'
        #    self.needlogin = True

        try:
            f = open('./metadata.xml', 'rb')
            self.metadata = boxdotnet.XMLNode.parseXML(f.read())
            print self.metadata.view[0]['ts']
        except IOError:
            print 'no file named metadata.xml'

    def sync(self):
        """not implemented yet"""
        """download newest metadata"""
        client_gd.retrieve_metadata()
        """compare  metas"""
        if self.metadata.view[0] == 0:
            self.metadata = client_gd.metadata
        """while loop starts"""
          """create folder"""
            """compare metadata lists, choose to upload or download according to the timestamp"""
              

    def init(self):
        """not implemented yet"""
        #if self.needlogin:
            #rsp = self.client_box.login(self.app_id)
            #self.token = rsp.auth_token[0].elementText
            #f = open('Token', 'wb')
            #f.write(self.token)
            #f.close()

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
            if not self.client_gd.Drive_Service:
                self.client_gd.authent()


def main():
    print 'app starts'
    cv = cloudview() 
    cv.init()

if __name__ == "__main__":
    main()
