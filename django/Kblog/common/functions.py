# -*- coding:utf-8 -*-
import sys, os, pprint, random, cgi, json, time, datetime, pytz , hashlib, magic
from Kblog.models import *
try:
    import xml.etree.cElementTree as ET 
except ImportError:
    import xml.etree.ElementTree as ET 

reload(sys)
sys.setdefaultencoding('utf-8') 
timeZone = pytz.timezone('Asia/Shanghai')
categoryRes = False
webInfo = False
navRes = False
themeConfs = False

def isset(v): 
    try : 
        type (eval(v)) 
    except : 
        return  0 
    else : 
        return  1


def getThemePath():
	currTheme = Options.objects.get(name='theme')
	return 'themes/' + currTheme.value + '/'

def getWebInfo():
    global webInfo
    if webInfo == False:
        webInfo = resetWebInfo()
    return webInfo

def resetWebInfo():
    detail = Options.objects.exclude(name__contains='theme')
    newDetail = {}
    for val in detail:
        newDetail[val.name] = val.value

    return newDetail

def getNavList():
    global navRes
    if navRes == False:
        navRes = getNavList()
	return navRes

def getNavList():
	navList = Category.objects.filter(pid=0).all()
	return navList

def getCategoryList(countType='&nbsp;'):
    global categoryRes
    if categoryRes == False:
		categoryRes = resetCategoryList(countType)
    return categoryRes

def resetCategoryList(countType):

	sql = 'SELECT category_id,name,pid,path,path||\'-\'||category_id AS bpath FROM "' + Meta.db_table + '_category" ORDER BY bpath'

	categoryList = Category.objects.raw(sql)
	categoryList = list(categoryList)

	for category in categoryList:
		countNbsp  = ''
		length     = int(len(category.bpath.split('-'))-2)*4

		for index in range(length):
			countNbsp += countType

		category.count = countNbsp

	return categoryList


def getProtocol(request):
	protocol = 'http://'
	if request.is_secure() == True:
		protocol = 'https://'
	return protocol


def checkLoginAdmin(userInfo):
	if (userInfo != False) and (userInfo['group'] == 'administrator'):
		return True
	else:
		return False


def getCurrTime():
    global timeZone
    return datetime.strftime(datetime.now(timeZone), '%Y-%m-%d %H:%M:%S')


def getTheme():
	currTheme = Options.objects.get(name='theme')
	return currTheme.value

def getThemesConfig():
    global themeConfs
    if themeConfs == False:
        themeConfs = scanThemesConfig()
    return themeConfs

def scanThemesConfig():
    index       = 0
    configList  = {}
    mydir       = os.path.split(os.path.realpath(__file__))[0] + '/../templates/themes/'

    for dirs in os.listdir(mydir):

        confPath = os.path.join(mydir, dirs)
        if os.path.isdir(confPath) and os.path.exists(confPath + '/config.xml'):

            try:
                tree = ET.parse(confPath + '/config.xml')
                root = tree.getroot()
            except Exception, e:
                print "Error:cannot parse file: config.xml"
                print e
                sys.exit(1)

            configList[index] = {}
            key = 0
            for child in root:
                configList[index][child.tag] = child.text
                key += 1

            index += 1
    return configList


def getSizeInNiceString(sizeInBytes):

    for (cutoff, label) in [(1024*1024*1024, 'GB'), (1024*1024, 'MB'), (1024, 'KB')]:

        if sizeInBytes >= cutoff:
            return '%.1f %s' % (sizeInBytes * 1.0 / cutoff, label)

    if sizeInBytes == 1:
        return '1 byte'
    else:
        bytes = '%.1f' % (sizeInBytes or 0,)
        return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'

def message(msg='', url=''):
	return u"alert('" + msg + "');window.location.href='" + url + "';"
