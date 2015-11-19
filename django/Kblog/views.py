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
import sys, os, pprint, random, cgi, json, time, datetime, pytz , hashlib, magic
from common import functions as C

reload(sys)
sys.setdefaultencoding('utf-8') 
timeZone = pytz.timezone('Asia/Shanghai')

def code(request):
    figures        = [2,3,4,5,6,7,8,9]
    ca             = Captcha(request)
    ca.words       = [''.join([str(random.sample(figures,1)[0]) for i in range(0,4)])]
    ca.type        = 'word'
    ca.img_width   = 100
    ca.img_height  = 30
    return ca.display()


def index(request):
    url = request.get_host()
    cid = request.GET.get('cid', 0)
    navList = C.getNavList()

    if request.method == 'POST':
		articleList = Article.objects.filter(title__icontains=cgi.escape(request.POST.get('word'))).order_by('-article_id')
    elif cid == 0:
		articleList = Article.objects.all().order_by('-article_id')
    else:
		sql = 'SELECT * FROM "' + Meta.db_table + '_article" AS article LEFT JOIN "' + Meta.db_table
		sql += '_relation" AS relation ON article.article_id=relation.aid WHERE relation.cid=' + cgi.escape(cid)
		#sql += " AND article.title LIKE '%%" + request.POST.get('word') + "%%'"
		sql += ' ORDER BY article_id DESC'
		articleList = Article.objects.raw(sql)
		articleList = list(articleList)
		
    paginator  = Paginator(articleList, 5)
    page       = int(request.GET.get('page', 1))
	
    try:
		pagebar = paginator.page(page)
    except PageNotAnInteger:
		pagebar = paginator.page(1)
    except EmptyPage:
		pagebar = paginator.page(paginator.num_pages)
		
    categoryList     = C.getCategoryList()
    userInfo         = request.session.get('uInfo', '')
    contentDateList  = Article.objects.order_by('created').values('created').distinct()
	
    context = {
		'url'              : url,
		'pagebar'          : pagebar,
		'navList'          : navList,
		'userinfo'         : userInfo,
		'cid'              : int(cid),
		'articleList'      : articleList,
        'categoryList'     : categoryList,
		'webInfo'          : C.getWebInfo(),
		'contentDateList'  : contentDateList,
		'themeHeader'      : C.getThemePath() + '/Public/header.html',
		'themeFooter'      : C.getThemePath() + '/Public/footer.html'
	}
    return render(request, C.getThemePath() + 'index.html', context)

def detail(request):
	
	aid = cgi.escape(request.GET.get('aid'))
	url = request.get_host()

	detail = []
	if C.isset(aid):
		detail = Article.objects.get(article_id=aid)
		detail.author  = User.objects.get(user_id=detail.author).username
		detail.content = detail.content.replace('\t', '').replace('\n', '').replace(' ', '')
	
	navList      = C.getNavList()
	userInfo     = request.session.get('uInfo', '')
	commentHtml  = commentTree(commentList, 0, False)
	commentList  = Comment.objects.filter(article_id=aid)

	del commentList

	upArticle = Article.objects.get(article_id=aid)
	upArticle.look_count = upArticle.look_count+1
	upArticle.save()

	context = {
		'userinfo'     : userInfo,
		'detail'       : detail,
		'navList'      : navList,
		'url'          : url,
        'aid'          : aid,
		'commentHtml'  : commentHtml,
		'themeHeader'  : C.getThemePath() + '/Public/header.html',
		'themeFooter'  : C.getThemePath() + '/Public/footer.html'
	}

	return render(request, C.getThemePath() + 'detail.html', context)

def comment_post(request):

    if request.method == 'POST':
        userId     = 0
        aid        = int(request.POST.get('aid', 0))
        upArticle  = Article.objects.get(article_id=aid)
        form       = CommentForm(request.POST)

        if form.is_valid():
            
            if C.isset(request.session.get('uInfo')):
                userId = request.session['uInfo']['user_id']

            status = Comment.objects.create(
			    article_id  = aid,
                status      = 'waiting',
				user_id     = int(userId),
			    ip          = getClientIp(request),
			    pid         = int(request.POST.get('pid', 0)),
			    agent       = request.META.get('HTTP_USER_AGENT', ''),
			    avatar      = cgi.escape(request.POST.get('avatar', '')),
			    comment     = cgi.escape(request.POST.get('comment', '')),
			    nickname    = cgi.escape(request.POST.get('nickname', ''))
		    )

            if status:
			    upArticle.comment_count = upArticle.comment_count+1
			    upArticle.save()

    return HttpResponse('success')

def checkaccount(request):
	response_data = {}  
	response_data['status'] = 0

	if request.method == 'GET':
		count = User.objects.filter(username=val).count()
		val   = cgi.escape(request.GET.get('val').lower())
		response_data['status'] = count

	return HttpResponse(json.dumps(response_data), content_type='application/json')  

def signup(request):

    form = None

    context = {
    	'themeHeader' : C.getThemePath() + '/Public/header.html',
		'themeFooter' : C.getThemePath() + '/Public/footer.html'
    }

    if request.method == 'POST':
        _code = request.POST.get('code') or ''
        if not _code:
            return render(C.getThemePath() + 'signup.html',locals())

        ca = Captcha(request)
        if not ca.check(_code):
            return render(request, C.getThemePath() + 'signup.html', {'error':'验证码错误'})

        context['form'] = SignupForm(request.POST)
        if context['form'].is_valid():
			exists = User.objects.filter(username=cgi.escape(request.POST.get('username'))).count()

			if exists > 0:
				return render(request, 'signup.html', {'error':'用户名已存在'})

			User.objects.create(
                status    = 1,
				group     = 'subscriber',
			    email     = cgi.escape(request.POST.get('email')),
			    username  = cgi.escape(request.POST.get('username').lower()),
                password  = make_password(cgi.escape(request.POST.get('upwd')), None, 'pbkdf2_sha256')
			)

			return HttpResponse('Success')

        else:
	        return render(request, C.getThemePath() + 'signup.html', context)

    else:
	    return render(request, C.getThemePath() + 'signup.html', context)

def signin(request):
    navList = C.getNavList()
    url     = request.get_host()
    context = {}
    context['themeHeader'] = C.getThemePath() + '/Public/header.html'
    context['themeFooter'] = C.getThemePath() + '/Public/footer.html'

    if request.method == 'POST':

        form = SigninForm(request.POST)
        if not form.is_valid():
			context['form'] = form
			return render(request, C.getThemePath() + 'signin.html', context)

        try:
            userinfo  = User.objects.get(username=request.POST.get('username', '').lower())
            password  = cgi.escape(request.POST.get('upwd'))
            status    = check_password(password, userinfo.password)
            username  = cgi.escape(request.POST.get('username', '').lower())
        except:
            context['error'] = '用户名或密码错误'
            return render(request, C.getThemePath() + 'signin.html', context)
		
        if status:
			request.session['uInfo']             = {}
			request.session['uInfo']['group']    = userinfo.group
			request.session['uInfo']['user_id']  = userinfo.user_id
			request.session['uInfo']['uname']    = userinfo.username
			return HttpResponseRedirect('/')

        else:
            context['error'] = '用户名或密码错误'
            return render(request, C.getThemePath() + 'signin.html', context)

    else:
        context['url']      = url
        context['navList']  = navList
        return render(request, C.getThemePath() + 'signin.html', context)

def logout(request):

    if request.session.get('uInfo', False) != False:
        del request.session['uInfo']

    context = {
        'themeHeader' : C.getThemePath() + '/Public/header.html',
        'themeFooter' : C.getThemePath() + '/Public/footer.html'
    }

    return render(request, C.getThemePath() + 'logout.html', context)

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

