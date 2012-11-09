#!/usr/bin/python

import boxdotnet

client = boxdotnet.BoxDotNet()

token = ''
needlogin = False

try:
    f = open('Token', 'rb')
    token = f.read();
    if token == '': 
        print 'we got nothing and we need to login'
        needlogin = True
    f.close()
except IOError:
    print 'no token file been established'
    needlogin = True
    
if needlogin:
    rsp = client.login('9cluykmx5i2filqz202p1t5frptgtjwn')
    token = rsp.auth_token[0].elementText
    f = open('Token', 'wb')
    f.write(token)
    f.close

client.upload('test.txt', auth_token=token, folder_id=0, share=1)
