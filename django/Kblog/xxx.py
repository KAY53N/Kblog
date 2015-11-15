# -*- coding:utf-8 -*-
import sys, os, pprint, random, cgi, json, time, datetime, pytz , hashlib, magic
try:
    import xml.etree.cElementTree as ET 
except ImportError:
    import xml.etree.ElementTree as ET 

import glob

def getThemesConfig():
    mydir = os.path.split(os.path.realpath(__file__))[0] + '/templates/themes/'
    index = 0
    configList = {}
    for dirs in os.listdir(mydir):
        confPath = os.path.join(mydir, dirs)
        if os.path.isdir(confPath) and os.path.exists(confPath + '/config.xml'):
            try:
                tree = ET.parse(confPath + '/config.xml')
                root = tree.getroot()
            except Exception, e:
                print "Error:cannot parse file:xxx.xml."
                print e
                sys.exit(1)
            configList[index] = {}
            key = 0
            for child in root:
                configList[index][child.tag] = child.text
                key += 1
            index += 1
    return configList
shit = getThemesConfig()
#print shit

for filename in glob.glob(r'/alidata/web/xujiantao.com/djproject/Kblog/templates/themes/default/*.html'):
	print filename

'''
for root,dirs,files in os.walk('/alidata/web/xujiantao.com/djproject/Kblog/templates/themes/default'):
	for file in files:
		if os.path.isfile(root + os.sep + file) and file.find('.html'):
			print root + os.sep + file
'''
'''
a = 'hello word'
a.replace('wosssrd','python')
print a
'''
