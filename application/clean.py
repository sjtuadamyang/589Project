#!/usr/bin/python
import os
from shutil import rmtree
from os import listdir
from os.path import isfile, join

os.system('./cloudview.py testcase/clean')

filekept = ['mount_command','unmount','CloudView','default','GOOGLE_CREDENTIAL', 'Token', 'boxdotnet.py', 'boxdotnet.pyc', \
'clean.py', 'client_box_test.py', 'cloudview.py', 'gdr_yyt.py', 'gdr_yyt.pyc', \
'testcase', '.gitignore', 'xmp.py', ''] 
onlyfiles = [f for f in listdir(os.path.dirname(os.path.realpath(__file__)))]

for i in onlyfiles:
    if not i in filekept:
        print "deleting local file "+i
        realpath = os.path.realpath(i)
        if os.path.isfile(realpath):
            os.remove(realpath)
        else:
            rmtree(realpath)


