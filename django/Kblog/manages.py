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
from django.template import RequestContext
from django.core.context_processors import csrf
import sys, os, pprint, random, cgi, json, time, datetime, pytz , hashlib, magic, glob
from common import functions as C

reload(sys)
sys.setdefaultencoding('utf-8') 
timeZone = pytz.timezone('Asia/Shanghai')
manageThemeDir = 'manage/'

def manage(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')
    else:
		context = {}
		articleCount = Article.objects.count()
		commentCount = Comment.objects.count()
		articleList = Article.objects.all().order_by('-article_id')[:5]
		commentList = Comment.objects.all().order_by('-comment_id')[:5]

		context = {
			'commentList'   : commentList,
			'articleList'   : articleList,
			'commentCount'  : commentCount,
			'articleCount'  : articleCount
		}
		return render(request, manageThemeDir + 'manage.html', context)


#=======================================#


def article(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

    context = {}
    searchCondition = ''
    keyword = cgi.escape(request.GET.get('word', ''))
    if C.isset(keyword):
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

	return render(request, manageThemeDir + 'article.html', context)


def article_write(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	userInfo  = request.session.get('uInfo', False)
	url       = C.getProtocol(request) + request.get_host()

	if C.checkLoginAdmin(userInfo) == False:
		return HttpResponseRedirect('/')

	if request.method == 'POST':
		currTime    = C.getCurrTime()
		createTime  = cgi.escape(request.POST.get('create_date')) + ' ' + cgi.escape(request.POST.get('create_time'))

		articleInfo = Article.objects.create(
			look_count     = 0,
			comment_count  = 0,
			update_time    = currTime,
			create_time    = createTime,
			author         = int(userInfo['user_id']),
			title          = cgi.escape(request.POST.get('title')),
			content        = cgi.escape(request.POST.get('content')),
			article_pic    = cgi.escape(request.POST.get('article_pic')),
			created        = datetime.datetime.strftime(datetime.datetime.now(timeZone), '%Y年%m月')
		)

		categoryIdList = request.REQUEST.getlist('category')
		for item in categoryIdList:
			Relation.objects.create(aid=articleInfo.article_id, cid=item)

	categoryList = C.getCategoryList()
	attachmentList = Attachment.objects.all().order_by('-attrch_id')
	context = {
		'url'             : url,
		'categoryList'    : categoryList,
		'attachmentList'  : attachmentList
	}
	return render(request, manageThemeDir + 'article_write.html', context)


def article_edit(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	context = {}
	url       = request.get_host()
	userInfo  = request.session.get('uInfo', False)
	aid       = cgi.escape(request.GET.get('aid', 0))
	
	if request.method == 'POST':

		updateArticle  = Article.objects.get(article_id=aid)
		createTime     = cgi.escape(request.POST.get('create_date')) + ' ' + cgi.escape(request.POST.get('create_time'))
		
		updateArticle.create_time  = createTime
		updateArticle.update_time  = C.getCurrTime()
		updateArticle.author       = int(userInfo['user_id'])
		updateArticle.article_pic  = request.POST.get('article_pic', '')
		updateArticle.title        = cgi.escape(request.POST.get('title', ''))
		updateArticle.content      = cgi.escape(request.POST.get('content', ''))
		updateArticle.save()

		Relation.objects.filter(aid=aid).delete()

		categoryIdList = cgi.escape(request.REQUEST.getlist('category'))

		for item in categoryIdList:
			Relation.objects.create(aid=aid, cid=item)

		return HttpResponse('修改文章成功')

	detail = []
	if C.isset(aid):
		detail = Article.objects.get(article_id=aid)
		detail.create_date  = str(detail.create_time)[0:10]
		detail.create_time  = str(detail.create_time)[10:16]
		detail.author       = User.objects.get(user_id=detail.author).username
		detail.content      = detail.content.replace('\t', '').replace('\n', '').replace(' ', '')

	categoryList    = C.getCategoryList()
	activeCategory  = Relation.objects.filter(aid=aid).all()
	attachmentList  = Attachment.objects.all().order_by('-attrch_id')

	context = {
		'detail'          : detail,
		'categoryList'    : categoryList,
		'activeCategory'  : activeCategory,
		'attachmentList'  : attachmentList
	}

	return render(request, manageThemeDir + 'article_edit.html', context)


def article_delete(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')
	idList = request.REQUEST.getlist('idlist')
	if len(idList) > 0:
		Article.objects.filter(article_id__in=idList).delete()
		Relation.objects.filter(aid__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')


#=======================================#


def file_upload(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponse('No signin')

	responseData = {}
	
	url = C.getProtocol(request) + request.get_host()

	reqfile  = request.FILES['upfile']
	suffix   = os.path.splitext(reqfile.name)
	suffix   = str(suffix[1].replace('.', '')).lower()
	
	img      = Image.open(reqfile)

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

	responseData['suffix']    = suffix
	responseData['status']    = 'success'
	responseData['savename']  = fileName,
	responseData['fileName']  = reqfile.name,
	responseData['url']       = url + savepath + fileName
	responseData['fileSize']  = C.getSizeInNiceString(fileSize)
	responseData['savepath']  = time.strftime('%Y/%m/',time.localtime(time.time())),
	
	userId = request.session.get('user_id', 0)

	Attachment.objects.create(
		suffix         = suffix,
		type           = 'image',
		savename       = fileName,
		update_time    = time.time(),
		create_time    = time.time(),
		user_id        = int(userId),
		original_name  = reqfile.name,
		size           = int(fileSize),
		savepath       = time.strftime('%Y/%m/', time.localtime(time.time()))
	)

	return HttpResponse(json.dumps(responseData), content_type='application/json')


def file_delete(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	responseData = {}
	responseData['status'] = 'faild'

	if request.method == 'POST':
		filename = os.path.dirname(__file__) + '/static/upload/' + request.POST.get('savepath').replace('.', '') + cgi.escape(request.POST.get('filename'))
		if os.path.isfile(filename):
			os.remove(filename)
			Attachment.objects.filter(savename=cgi.escape(request.POST.get('filename'))).delete()
			responseData['status'] = 'success'
	return HttpResponse(json.dumps(responseData), content_type='application/json')


#=======================================#


def comment(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	context       = {}
	cid           = int(request.GET.get('cid', 0))
	status        = cgi.escape(request.GET.get('status', 'pass'))
	updateStatus  = cgi.escape(request.GET.get('update_status', ''))

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
			'msg' : C.message(msg, '/manage_comment/?status=' + str(status))
		}

		return render(request, manageThemeDir + 'comment.html', context)
	
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
		'status'   : status,
		'pagebar'  : pagebar
	}

	return render(request, manageThemeDir + 'comment.html', context)

def comment_delete(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')
	idList = request.REQUEST.getlist('idlist')
	if len(idList) > 0:
		Comment.objects.filter(comment_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')


#=======================================#


def category(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	context = {
		'categoryList' : C.getCategoryList('<i class="uk-icon-minus"></i>')
	}

	return render(request, manageThemeDir + 'category.html', context)

def category_add(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')
	context = {}
	if request.method == 'POST':

		chosenPid  = int(request.POST.get('pid', 0))
		pidInfo    = Category.objects.get(category_id=chosenPid)
		currPath   = str(pidInfo.path) + '-' + str(pidInfo.category_id)
		
		Category.objects.create(
			path  = currPath,
			pid   = chosenPid,
			name  = cgi.escape(request.POST.get('name', '')),
		)

		return HttpResponse('success')
	
	context = {
		'categoryList' : C.getCategoryList()
	}

	return render(request, manageThemeDir + 'category_add.html', context)


def category_edit(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')
	context  = {}
	cid      = int(request.GET.get('cid'))
	detail   = Category.objects.get(category_id=cid)

	if detail.pid > 0:
		detail.pname = Category.objects.get(category_id=detail.pid).name
	else:
		detail.pname = '顶级分类'
	
	context = {
		'detail' : detail
	}
	
	return render(request, manageThemeDir + 'category_edit.html', context)


def category_delete(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')
	idList = request.REQUEST.getlist('idlist')
	if len(idList) > 0:
		Category.objects.filter(category_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')


#=======================================#


def attachment(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

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

	paginator  = Paginator(attachmentList, 10)
	page       = int(request.GET.get('page', 1))

	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)

	for item in pagebar:
		item.size = C.getSizeInNiceString(int(item.size))
		item.create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.create_time))

	context = {
		'word'     : word,
		'pagebar'  : pagebar
	}

	return render(request, manageThemeDir + 'attachment.html', context)


def attachment_delete(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	idList = request.REQUEST.getlist('idlist')
	if len(idList) > 0:
		Attachment.objects.filter(attrch_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')


#=======================================#


def user(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	context = {}
	if request.GET.get('word'):
		userList = User.objects.filter(username__icontains=cgi.escape(request.GET.get('word'))).order_by('-user_id')
	else:
		userList = User.objects.all()

	paginator  = Paginator(userList, 10)
	page       = int(request.GET.get('page', 1))

	try:
		pagebar = paginator.page(page)
	except PageNotAnInteger:
		pagebar = paginator.page(1)
	except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)
	
	context = {
		'pagebar' : pagebar
	}

	return render(request, manageThemeDir + 'user.html', context)


def user_add(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	if request.method == 'POST':
		email     = request.POST.get('email', '')
		group     = cgi.escape(request.POST.get('group', ''))
		status    = cgi.escape(request.POST.get('status', ''))
		username  = cgi.escape(request.POST.get('username', ''))
		password  = make_password(cgi.escape(request.POST.get('password', '')), None, 'pbkdf2_sha256')

		User.objects.create(
			email     = email,
			group     = group,
			status    = status,
			username  = username,
			password  = password
		)

		return HttpResponse('Create User success')

	return render(request, manageThemeDir + 'user_add.html')


def user_edit(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

    context  = {}
    uid      = int(request.GET.get('uid', 0))

    if request.method == 'POST':
        updateUser = User.objects.get(user_id=request.POST.get('uid', 0))
        if request.POST.get('password') != '':
            updateUser.password = make_password(cgi.escape(request.POST.get('password')), None, 'pbkdf2_sha256')

        updateUser.email   = cgi.escape(request.POST.get('email'))
        updateUser.group   = cgi.escape(request.POST.get('group'))
        updateUser.status  = cgi.escape(request.POST.get('status'))
        updateUser.save()

        return HttpResponse('修改用户资料成功')

    context['detail'] = User.objects.get(user_id=uid)
    return render(request, manageThemeDir + 'user_edit.html', context)


def user_delete(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	idList = request.REQUEST.getlist('idlist')
	if len(idList) > 0:
		User.objects.filter(user_id__in=idList).delete()
		return HttpResponse('delete success')
	return HttpResponse('delete faild')


#=======================================#


def themes(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	context = {
		'currTheme'   : C.getTheme(),
		'configList'  : C.getThemesConfig()
	}

	return render(request, manageThemeDir + 'themes.html', context)


def theme_swich(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

    opt = Options.objects.get(name='theme')
    opt.value = cgi.escape(request.POST.get('change'))
    opt.save()
    return HttpResponseRedirect('/manage_themes/')


def theme_edit(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

    if request.GET.get('file'):
        fileName = cgi.escape(request.GET.get('file').replace('..', '').replace('/', '').replace('%', ''))
    else:
        fileName = 'index.html'
    if request.GET.get('theme'):
        themeDir = 'themes/' + cgi.escape(request.GET.get('theme').replace('.', '')) + '/'
    else:
        themeDir = C.getThemePath()

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
        'content'   : content,
        'fileList'  : fileList,
		'fileName'  : fileName,
        'themeDir'  : themeDir
    }

    return render(request, manageThemeDir + 'theme_edit.html', context)


def theme_changfile(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

    if request.method == 'POST':
        themeDir = cgi.escape(request.POST.get('themeDir').replace('.', ''))
        f = open(os.path.split(os.path.realpath(__file__))[0] + '/templates/' + themeDir + cgi.escape(request.POST.get('file')), 'w')
        f.write(request.POST.get('content'))
        f.close()
    return HttpResponse('ok')


#=======================================#


def manage_profile(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

	msg = ''
	if request.method == 'POST':
		userInfo = User.objects.get(username='admini')
		password = make_password(cgi.escape(request.POST.get('upwd', '')), None, 'pbkdf2_sha256')
		
		userInfo.password = password
		status = userInfo.save()
		
		if status:
			msg = message(u'修改成功', '/manage_profile')
		else:
			msg = message(u'修改失败', '/manage_profile')
	
	return render(request, manageThemeDir + 'profile.html', {msg:msg})


def manage_option(request):
    if C.checkLoginAdmin(request.session.get('uInfo', False)) == False:
        return HttpResponseRedirect('/signin/')

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

    return render(request, manageThemeDir + 'option.html', context)

def test(request):
    return HttpResponse(request.session['uInfo']['uname'])
