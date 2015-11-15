# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.template import Context, loader
from django.http import HttpResponse
from Kblog.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from DjangoCaptcha import Captcha
from django.contrib.auth.hashers import make_password, check_password
from PIL import Image
from django.template import RequestContext
from django.core.context_processors import csrf
import sys, os, pprint, random, cgi, json, time, datetime, pytz , hashlib, magic, glob
try:
    import xml.etree.cElementTree as ET 
except ImportError:
    import xml.etree.ElementTree as ET 


reload(sys)
sys.setdefaultencoding('utf-8') 
timeZone = pytz.timezone('Asia/Shanghai')
manageThemeDir = 'manage/'

def code(request):
    figures         = [2,3,4,5,6,7,8,9]
    ca              = Captcha(request)
    ca.words        = [''.join([str(random.sample(figures,1)[0]) for i in range(0,4)])]
    ca.type         = 'word'
    ca.img_width    = 100
    ca.img_height   = 30
    return ca.display()

def isset(v): 
    try : 
        type (eval(v)) 
    except : 
        return  0 
    else : 
        return  1

def getTheme():
	currTheme = Options.objects.get(name='theme')
	return currTheme.value

def getThemePath():
	currTheme = Options.objects.get(name='theme')
	return 'themes/' + currTheme.value + '/'

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

def getWebInfo():
    detail = Options.objects.exclude(name__contains='theme')
    newDetail = {}
    for val in detail:
        newDetail[val.name] = val.value
    return newDetail

def index(request):
	url = request.get_host()
	cid = cgi.escape(request.GET.get('cid'))
	if isset(cid) == 0:
		cid = 0
	navList = getNavList()
	if request.method == 'POST':
		articleList = Article.objects.filter(title__icontains=cgi.escape(request.POST.get('word'))).order_by('-article_id')
	elif cid == 0:
		articleList = Article.objects.all().order_by('-article_id')
	else:
		sql = 'SELECT * FROM "' + Meta.db_table + '_article" AS article LEFT JOIN "' + Meta.db_table
		sql += '_relation" AS relation ON article.article_id=relation.aid WHERE relation.cid=' + str(cid)
		#sql += " AND article.title LIKE '%%" + request.POST.get('word') + "%%'"
		sql += ' ORDER BY article_id DESC'
		articleList = Article.objects.raw(sql)
		articleList = list(articleList)
	paginator = Paginator(articleList, 5)
	page = int(request.GET.get('page', 1))
	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)
	userInfo = request.session.get('uInfo', '')
	categoryList = getCategoryList()

	contentDateList = Article.objects.order_by('created').values('created').distinct()
	context = {
		'userinfo':userInfo,
		'navList':navList,
		'cid':int(cid),
		'articleList':articleList,
		'url':url,
        'categoryList':categoryList,
		'contentDateList':contentDateList,
		'pagebar':pagebar,
		'webInfo' : getWebInfo(),
		'themeHeader':getThemePath() + '/Public/header.html',
		'themeFooter':getThemePath() + '/Public/footer.html'
	}

	return render(request, getThemePath() + 'index.html', context)

def detail(request):
	aid = cgi.escape(request.GET.get('aid'))
	url = request.get_host()
	detail = []
	if isset(aid):
		detail = Article.objects.get(article_id=aid)
		detail.author = User.objects.get(user_id=detail.author).username
		detail.content = detail.content.replace('\t', '').replace('\n', '').replace(' ', '')
	commentList = Comment.objects.filter(article_id=aid)
	commentHtml = commentTree(commentList, 0, False)
	navList = getNavList()
	userInfo = request.session.get('uInfo', '')

	del commentList

	upArticle = Article.objects.get(article_id=aid)
	msg = ''
	if request.method == 'POST':

		form = CommentForm(request.POST)
		if not form.is_valid():
			context = {
				'form':form,
				'userinfo':userInfo,
				'detail':detail,
				'navList':navList,
				'url':url,
				'commentHtml':commentHtml
			}
			return render(request, 'detail.html', context)

		userId = request.session['uInfo']['user_id']
		status = Comment.objects.create(
			user_id = int(userId),
			nickname = cgi.escape(request.POST.get('nickname')),
			avatar = cgi.escape(request.POST.get('avatar')),
			comment = cgi.escape(request.POST.get('comment')),
			agent = request.META.get('HTTP_USER_AGENT', ''),
			ip = getClientIp(request),
			pid = cgi.escape(request.POST.get('pid')),
			article_id = aid,
			status = 'waiting'
		)
		if status:
			upArticle.comment_count = upArticle.comment_count+1
			upArticle.save()
			msg = message(u'评论成功', '/detail/?aid=' + str(aid))
		else:
			msg = message(u'评论失败', '/detail/?aid=' + str(aid))

	upArticle.look_count = upArticle.look_count+1
	upArticle.save()

	context = {
		'msg':msg,
		'userinfo':userInfo,
		'detail':detail,
		'navList':navList,
		'url':url,
		'commentHtml':commentHtml,
		'themeHeader':getThemePath() + '/Public/header.html',
		'themeFooter':getThemePath() + '/Public/footer.html'
	}

	return render(request, getThemePath() + 'detail.html', context)

def checkaccount(request):
	response_data = {}  
	response_data['status'] = 0

	if request.method == 'GET':
		val = cgi.escape(request.GET.get('val').lower())
		count = User.objects.filter(username=val).count()
		response_data['status'] = count

	return HttpResponse(json.dumps(response_data), content_type='application/json')  

def signup(request):
    form = None
    context = {
    	'themeHeader':getThemePath() + '/Public/header.html',
		'themeFooter':getThemePath() + '/Public/footer.html'
    }
    if request.method == 'POST':
        _code = request.POST.get('code') or ''
        if not _code:
            return render('signup.html',locals())
        ca = Captcha(request)
        if not ca.check(_code):
            return render(request, 'signup.html', {'error':'验证码错误'})
        context['form'] = SignupForm(request.POST)
        if context['form'].is_valid():
			exists = User.objects.filter(username=cgi.escape(request.POST.get('username'))).count()
			if exists > 0:
				return render(request, 'signup.html', {'error':'用户名已存在'})
			User.objects.create(
			    username = cgi.escape(request.POST.get('username').lower()),
			    email = cgi.escape(request.POST.get('email')),
                password = make_password(cgi.escape(request.POST.get('upwd')), None, 'pbkdf2_sha256'),
				group = 'subscriber',
                status = 1
			)
			return HttpResponse('Success')
        else:
	        return render(request, getThemePath() + 'signup.html', context)
    else:
	    return render(request, getThemePath() + 'signup.html', context)

def signin(request):
	url = request.get_host()
	navList = getNavList()
	if request.method == 'POST':
		form = SigninForm(request.POST)
		if not form.is_valid():
			return render(request, getThemePath() + 'signin.html', {'form':form})
		try:
			username = cgi.escape(request.POST.get('username').lower())
			password = cgi.escape(request.POST.get('upwd'))
			userinfo = User.objects.get(username=username)
			status = check_password(password, userinfo.password)
		except :
			return render(request, getThemePath() + 'signin.html', {'error':'用户名或密码错误'})
		
		if status:
			request.session['uInfo'] = {}
			request.session['uInfo']['uname'] = userinfo.username
			request.session['uInfo']['user_id'] = userinfo.user_id
			request.session['uInfo']['group'] = userinfo.group
			return HttpResponseRedirect('/')
		else:
			return render(request, getThemePath() + 'signin.html', {'error':'用户名或密码错误'})
	else:
		context = {
			'navList':navList,
			'url':url,
            'themeHeader':getThemePath() + '/Public/header.html',
            'themeFooter':getThemePath() + '/Public/footer.html'
		}
		return render(request, getThemePath() + 'signin.html', context)

def logout(request):
    if request.session.get('uInfo', False) != False:
        del request.session['uInfo']
    context = {
        'themeHeader':getThemePath() + '/Public/header.html',
        'themeFooter':getThemePath() + '/Public/footer.html'
    }
    return render(request, getThemePath() + 'logout.html', context)

def comment_post(request):
	return HttpResponseRedirect('/')
	
def getClientIp(request):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):  
		return cgi.escape(request.META['HTTP_X_FORWARDED_FOR'])
    else:  
        return cgi.escape(request.META['REMOTE_ADDR'])

def commentTree(data, pid, nested=False):
	html = ''
	for item in data:
		if nested == True and item.pid == pid:
			html += '<ul>'
		if item.pid == pid:
			html += '<li><article class="uk-comment"><header class="uk-comment-header">'
			html += '<img width="50" height="50" alt="" src="/static/images/avatars/' + item.avatar + '" class="uk-comment-avatar">'
			html += '<h4 class="uk-comment-title">' + str(item.nickname).decode('utf-8') + '</h4>'
			html += '<p class="uk-comment-meta">' + str(item.create_time) + ' | '
			html += '<a href="#commentForm" class="uk-button uk-button-mini uk-button-success reply" nickname="'
			html += str(item.nickname).decode('utf-8') + '" id="' + str(item.comment_id) +'">Reply</a> | #</p></header>'
			html += '<div class="uk-comment-body word_wrap">' + item.comment + '</div>'
			html += '</article></li>'
			html += commentTree(data, item.comment_id, True)
		if nested == True and item.pid == pid:
			html += '</ul>'
	return html

def message(msg='', url=''):
	return u"alert('" + msg + "');window.location.href='" + url + "';"

def manage(request):
	articleCount = Article.objects.count()
	commentCount = Comment.objects.count()
	articleList = Article.objects.all().order_by('-article_id')[:5]
	commentList = Comment.objects.all().order_by('-comment_id')[:5]
	context = {
		'articleCount':articleCount,
		'commentCount':commentCount,
		'articleList':articleList,
		'commentList':commentList
	}
	return render(request, manageThemeDir + 'manage.html', context)

def manage_profile(request):
	userInfo = request.session.get('uInfo', False)
	if checkLoginAdmin(userInfo) == False:
		return HttpResponseRedirect('/')

	msg = ''
	if request.method == 'POST':
		password = make_password(cgi.escape(request.POST.get('upwd')), None, 'pbkdf2_sha256')
		userInfo = User.objects.get(username='admini')
		userInfo.password = password
		status = userInfo.save()
		if status:
			msg = message(u'修改成功', '/manage_profile')
		else:
			msg = message(u'修改失败', '/manage_profile')
	return render(request, manageThemeDir + 'manage_profile.html', {msg:msg})

def manage_write(request):
	url = getProtocol(request) + request.get_host()

	userInfo = request.session.get('uInfo', False)
	if checkLoginAdmin(userInfo) == False:
		return HttpResponseRedirect('/')

	if request.method == 'POST':
		currTime = getCurrTime()
		createTime = cgi.escape(request.POST.get('create_date')) + ' ' + cgi.escape(request.POST.get('create_time'))
		articleInfo = Article.objects.create(
			author = int(userInfo['user_id']),
			title = cgi.escape(request.POST.get('title')),
			content = cgi.escape(request.POST.get('content')),
			look_count = 0,
			comment_count = 0,
			article_pic = cgi.escape(request.POST.get('article_pic')),
			update_time = currTime,
			create_time = createTime,
			created =  datetime.datetime.strftime(datetime.datetime.now(timeZone), '%Y年%m月')
		)

		categoryIdList = cgi.escape(request.REQUEST.getlist('category'))
		for item in categoryIdList:
			Relation.objects.create(aid=articleInfo.article_id, cid=item)

	categoryList = getCategoryList()
	attachmentList = Attachment.objects.all().order_by('-attrch_id')
	context = {
		'url':url,
		'categoryList':categoryList,
		'attachmentList':attachmentList
	}
	return render(request, manageThemeDir + 'manage_write.html', context)

def getCategoryList(countType='&nbsp;'):
	sql = 'SELECT category_id,name,pid,path,path||\'-\'||category_id AS bpath FROM "' + Meta.db_table + '_category" ORDER BY bpath'
	categoryList = Category.objects.raw(sql)
	categoryList = list(categoryList)
	for category in categoryList:
		length = int(len(category.bpath.split('-'))-2)*4
		countNbsp = ''
		for index in range(length):
			countNbsp += countType
		category.count = countNbsp
	return categoryList

def getSizeInNiceString(sizeInBytes):
    for (cutoff, label) in [(1024*1024*1024, 'GB'), (1024*1024, 'MB'), (1024, 'KB')]:
        if sizeInBytes >= cutoff:
            return '%.1f %s' % (sizeInBytes * 1.0 / cutoff, label)

    if sizeInBytes == 1:
        return '1 byte'
    else:
        bytes = '%.1f' % (sizeInBytes or 0,)
        return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'

def manage_upload(request):
	responseData = {}
	url = getProtocol(request) + request.get_host()

	reqfile = request.FILES['upfile']
	suffix = os.path.splitext(reqfile.name)
	suffix = str(suffix[1].replace('.', '')).lower()
	
	img = Image.open(reqfile)
	img.thumbnail((800, 800), Image.ANTIALIAS)
	
	fileName = str(time.time()).replace('.', '') + str(random.randint(100, 9999))
	m2 = hashlib.md5() 
	m2.update(fileName)
	fileName = str(m2.hexdigest() + '.' + suffix)
	fileName = fileName[10:]

	savepath = '/static/upload/' + time.strftime('%Y/%m/',time.localtime(time.time()))
	filePath = os.path.dirname(__file__) + savepath
	if os.path.exists(filePath) == False:
		os.makedirs(filePath)
	filePath = filePath + fileName.lower()

	img.convert('RGB').save(filePath)

	fileSize = os.path.getsize(filePath)

	responseData['status'] = 'success'
	responseData['url'] = url + savepath + fileName
	responseData['fileName'] = reqfile.name,
	responseData['savename'] = fileName,
	responseData['savepath'] = time.strftime('%Y/%m/',time.localtime(time.time())),
	responseData['fileSize'] = getSizeInNiceString(fileSize)
	responseData['suffix'] = suffix
	
	userId = request.session.get('user_id', 0)
	Attachment.objects.create(
		user_id = int(userId),
		original_name = reqfile.name,
		type = 'image',
		size = int(fileSize),
		savepath = time.strftime('%Y/%m/',time.localtime(time.time())),
		savename = fileName,
		suffix = suffix,
		update_time = time.time(),
		create_time = time.time()
	)

	return HttpResponse(json.dumps(responseData), content_type='application/json')

def manage_deletefile(request):
	responseData = {}
	responseData['status'] = 'faild'
	if request.method == 'POST':
		filename = os.path.dirname(__file__) + '/static/upload/' + request.POST.get('savepath').replace('.', '') + cgi.escape(request.POST.get('filename'))
		if os.path.isfile(filename):
			os.remove(filename)
			Attachment.objects.filter(savename=cgi.escape(request.POST.get('filename'))).delete()
			responseData['status'] = 'success'
	return HttpResponse(json.dumps(responseData), content_type='application/json')

def manage_article(request):
	context = {}

	userInfo = request.session.get('uInfo', False)
	if checkLoginAdmin(userInfo) == False:
		return HttpResponseRedirect('/')

	searchCondition = ''
	keyword = request.GET.get('word')
	if isset(keyword):
		cgi.escape(keyword)
		searchCondition += " WHERE article.title LIKE '%%" + keyword + "%%' "

	sql = 'SELECT article_id, title, username AS author, name AS category FROM "' + Meta.db_table + '_article" AS article '
	sql += 'LEFT JOIN "' + Meta.db_table + '_relation" AS relation ON article.article_id=relation.aid '
	sql += 'LEFT JOIN "' + Meta.db_table + '_category" AS category ON relation.cid=category.category_id '
	sql += 'LEFT JOIN "' + Meta.db_table + '_user" AS usertab ON article.author=usertab.user_id '
	sql += searchCondition + 'ORDER BY article_id DESC'

	articleList = list(Article.objects.raw(sql))

	paginator = Paginator(articleList, 10)
	page = int(request.GET.get('page', 1))
	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)
	
	context = {
			'pagebar' : pagebar
	}

	return render(request, manageThemeDir + 'manage_article.html', context)

def manage_delarticle(request):
	idList = cgi.escape(request.REQUEST.getlist('idlist'))
	if len(idList) > 0:
		Article.objects.filter(article_id__in=idList).delete()
		Relation.objects.filter(aid__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')

def manage_editarticle(request):
	context = {}
	aid = cgi.escape(request.GET.get('aid'))
	url = request.get_host()
	userInfo = request.session.get('uInfo', False)
	
	if request.method == 'POST':
		updateArticle = Article.objects.get(article_id=aid)
		
		createTime = cgi.escape(request.POST.get('create_date')) + ' ' + cgi.escape(request.POST.get('create_time'))
		
		updateArticle.author = int(userInfo['user_id'])
		updateArticle.title = cgi.escape(request.POST.get('title'))
		updateArticle.content = cgi.escape(request.POST.get('content'))
		updateArticle.article_pic = request.POST.get('article_pic')
		updateArticle.update_time = getCurrTime()
		updateArticle.create_time = createTime
		updateArticle.save()

		Relation.objects.filter(aid=aid).delete()
		categoryIdList = cgi.escape(request.REQUEST.getlist('category'))
		for item in categoryIdList:
			Relation.objects.create(aid=aid, cid=item)

		return HttpResponse('修改文章成功')

	detail = []
	if isset(aid):
		detail = Article.objects.get(article_id=aid)
		detail.author = User.objects.get(user_id=detail.author).username
		detail.content = detail.content.replace('\t', '').replace('\n', '').replace(' ', '')
		detail.create_date = str(detail.create_time)[0:10]
		detail.create_time = str(detail.create_time)[10:16]

	categoryList = getCategoryList()
	attachmentList = Attachment.objects.all().order_by('-attrch_id')
	activeCategory = Relation.objects.filter(aid=aid).all()

	context = {
		'detail':detail,
		'categoryList':categoryList,
		'attachmentList':attachmentList,
		'activeCategory':activeCategory
	}
	return render(request, manageThemeDir + 'manage_editarticle.html', context)

def manage_comment(request):
	context = {}

	status = cgi.escape(request.GET.get('status', 'pass'))
	updateStatus = cgi.escape(request.GET.get('update_status', ''))
	cid = int(request.GET.get('cid', 0))
	if updateStatus != '' and cid != 0:
		res = False
		if updateStatus == 'delete':
			res = Comment.objects.filter(comment_id=cid).delete()
		else:
			upComment = Comment.objects.get(comment_id=cid)
			upComment.status = updateStatus
			res = upComment.save()

		msg = u'操作成功'
		if res == False:
			msg = u'操作失败'
		context = {
			'msg' : message(msg, '/manage_comment/?status=' + str(status))
		}
		return render(request, manageThemeDir + 'manage_comment.html', context)
	
	if status == 'pass':
		commentList = Comment.objects.filter(status='approved').order_by('-comment_id').all()
	else:
		commentList = Comment.objects.filter(status='waiting').order_by('-comment_id').all()

	paginator = Paginator(commentList, 10)
	page = int(request.GET.get('page', 1))
	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)

	articleList = []
	if pagebar:
		aidList = []
		for item in pagebar:
			aidList.append(item.article_id)
		articleList = Article.objects.filter(article_id__in=aidList).all()
		
	for item in pagebar:
		for it in articleList:
			if item.article_id == it.article_id:
				item.article = it.title

	context = {
		'pagebar' : pagebar,
		'status'  : status
	}

	return render(request, manageThemeDir + 'manage_comment.html', context)

def manage_delcomment(request):
	idList = cgi.escape(request.REQUEST.getlist('idlist'))
	if len(idList) > 0:
		Comment.objects.filter(comment_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')

def manage_category(request):
	context = {}
	
	'''
	categoryList = Category.objects.all()
	paginator = Paginator(categoryList, 10)
	page = int(request.GET.get('page', 1))
	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)
	
	context = {
		'pagebar':pagebar
	}
	'''

	context = {
		'categoryList' : getCategoryList('<i class="uk-icon-minus"></i>')
	}

	return render(request, manageThemeDir + 'manage_category.html', context)

def manage_addcategory(request):
	context = {}
	
	if request.method == 'POST':
		chosenPid = int(request.POST.get('pid'))
		pidInfo = Category.objects.get(category_id=chosenPid)
		currPath = str(pidInfo.path) + '-' + str(pidInfo.category_id)
		
		Category.objects.create(
			name = cgi.escape(request.POST.get('name')),
			pid = chosenPid,
			path = currPath
		)

		return HttpResponse('success')
	
	categoryList = getCategoryList()
	context = {
		'categoryList':categoryList		
	}

	return render(request, manageThemeDir + 'manage_addcategory.html', context)

def manage_editcategory(request):
	context = {}
	cid = int(request.GET.get('cid'))
	detail = Category.objects.get(category_id=cid)
	if detail.pid > 0:
		detail.pname = Category.objects.get(category_id=detail.pid).name
	else:
		detail.pname = '顶级分类'
	context = {
		'detail' : detail
	}
	return render(request, manageThemeDir + 'manage_editcategory.html', context)

def manage_delcategory(request):
	idList = cgi.escape(request.REQUEST.getlist('idlist'))
	if len(idList) > 0:
		Category.objects.filter(category_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')

def manage_attachment(request):
	context = {}
	sql = 'SELECT username, attrch_id, original_name, create_time, size '
	sql += 'FROM "' + Meta.db_table + '_attachment" AS attach LEFT JOIN "' + Meta.db_table +'_user" AS userx '
	sql += 'ON userx.user_id=attach.user_id '
	
	word = ''
	if request.GET.get('word'):
		word = str(cgi.escape(request.GET.get('word')))
		sql += "WHERE attach.original_name LIKE '%%" + str(cgi.escape(request.GET.get('word'))) + "%%' "

	sql += 'ORDER BY attrch_id DESC'
	
	attachmentList = Attachment.objects.raw(sql)
	attachmentList = list(attachmentList)

	paginator = Paginator(attachmentList, 10)
	page = int(request.GET.get('page', 1))
	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)

	for item in pagebar:
		item.size = getSizeInNiceString(int(item.size))
		item.create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.create_time))

	context = {
		'pagebar':pagebar,
		'word'   :word
	}

	return render(request, manageThemeDir + 'manage_attachment.html', context)

def manage_delattachment(request):
	idList = cgi.escape(request.REQUEST.getlist('idlist'))
	if len(idList) > 0:
		Attachment.objects.filter(attrch_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')


def manage_user(request):
	context = {}
	
	if request.GET.get('word'):
		userList = User.objects.filter(username__icontains=cgi.escape(request.GET.get('word'))).order_by('-user_id')
	else:
		userList = User.objects.all()

	paginator = Paginator(userList, 10)
	page = int(request.GET.get('page', 1))
	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)
	
	context = {
		'pagebar':pagebar
	}

	return render(request, manageThemeDir + 'manage_user.html', context)

def manage_adduser(request):
	if request.method == 'POST':
		username = cgi.escape(request.POST.get('username'))
		password = make_password(cgi.escape(request.POST.get('password')), None, 'pbkdf2_sha256')
		email = request.POST.get('email')
		group = cgi.escape(request.POST.get('group'))
		status = cgi.escape(request.POST.get('status'))

		User.objects.create(
			username = username,
			password = password,
			email = email,
			group = group,
			status = status
		)

		return HttpResponse('Create User success')

	return render(request, manageThemeDir + 'manage_adduser.html')

def manage_edituser(request):
	context = {}
	uid = int(request.GET.get('uid'))
	
	if request.method == 'POST':
		updateUser = User.objects.get(user_id=int(request.POST.get('uid')))
		if request.POST.get('password') != '':
			updateUser.password = make_password(cgi.escape(request.POST.get('password')), None, 'pbkdf2_sha256')
		
		updateUser.email = cgi.escape(request.POST.get('email'))
		updateUser.group = cgi.escape(request.POST.get('group'))
		updateUser.status = cgi.escape(request.POST.get('status'))
		updateUser.save()

		return HttpResponse('修改用户资料成功')

	detail = []
	if isset(uid):
		detail = User.objects.get(user_id=uid)

	context = {
		'detail':detail
	}
	return render(request, manageThemeDir + 'manage_edituser.html', context)

def manage_deluser(request):
	idList = cgi.escape(request.REQUEST.getlist('idlist'))
	if len(idList) > 0:
		User.objects.filter(user_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')

def manage_themes(request):
	context = {
		'currTheme' : getTheme(),
		'configList' : getThemesConfig()
	}
	return render(request, manageThemeDir + 'manage_themes.html', context)

def manage_uptheme(request):
    opt = Options.objects.get(name='theme')
    opt.value = cgi.escape(request.POST.get('change'))
    opt.save()
    return HttpResponseRedirect('/manage_themes/')

def manage_edittheme(request):
    if request.GET.get('file'):
        fileName = cgi.escape(request.GET.get('file').replace('..', '').replace('/', '').replace('%', ''))
    else:
        fileName = 'index.html'
    if request.GET.get('theme'):
        themeDir = 'themes/' + cgi.escape(request.GET.get('theme').replace('.', '')) + '/'
    else:
        themeDir = getThemePath()

    fileList = []
    for filename in glob.glob(os.path.split(os.path.realpath(__file__))[0] + '/templates/' + themeDir + '*.*ml'):
        p,f=os.path.split(filename);
        fileList.append(f)   

	file_object = open(os.path.split(os.path.realpath(__file__))[0] + '/templates/' + themeDir + fileName)
    try:
        content = file_object.read()
    finally:
        file_object.close()

    context = {
        'content':content,
        'fileList':fileList,
		'fileName':fileName,
        'themeDir':themeDir
    }
    return render(request, manageThemeDir + 'manage_edittheme.html', context)
def manage_writefile(request):
    if request.method == 'POST':
        themeDir = cgi.escape(request.POST.get('themeDir').replace('.', ''))
        f = open(os.path.split(os.path.realpath(__file__))[0] + '/templates/' + themeDir + cgi.escape(request.POST.get('file')), 'w')
        f.write(request.POST.get('content'))
        f.close()
    return HttpResponse('ok')
def getProtocol(request):
	protocol = 'http://'
	if request.is_secure() == True:
		protocol = 'https://'
	return protocol

def getNavList():
	navList = Category.objects.filter(pid=0).all()
	return navList

def checkLoginAdmin(userInfo):
	if (userInfo != False) and (userInfo['group'] == 'administrator'):
		return True
	else:
		return False

def manage_option(request):
    if request.method == 'POST':
        for key,val in request.POST.iteritems():
            if key != 'csrfmiddlewaretoken':
                #sql += 'INSERT INTO "' + Meta.db_table + '_options" VALUES(\'' + key + '\', \'' + val + '\') ON DUPLICATE KEY UPDATE value=\'' + val + '\';'
                options = Options.objects.get(name=cgi.escape(key))
                options.value = cgi.escape(val)
                options.save()
        return HttpResponse('success')
    detail = Options.objects.exclude(name__contains='theme')
    newDetail = {}
    for val in detail:
        newDetail[val.name] = val.value
    context = {
        'detail' : newDetail
    }
    return render(request, manageThemeDir + 'manage_option.html', context)

def getCurrTime():
	return datetime.datetime.strftime(datetime.datetime.now(timeZone), '%Y-%m-%d %H:%M:%S')

def test(request):
    return HttpResponse('...')
