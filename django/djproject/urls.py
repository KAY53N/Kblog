from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'Kblog.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^detail/', 'Kblog.views.detail', name='detail'),
    url(r'^signup/', 'Kblog.views.signup', name='signup'),
    url(r'^signin/', 'Kblog.views.signin', name='signin'),
	url(r'^code/', 'Kblog.views.code'),
	url(r'^logout/', 'Kblog.views.logout'),
	url(r'^comment_post/', 'Kblog.views.comment_post'),
	url(r'^checkaccount/', 'Kblog.views.checkaccount'),
	url(r'^manage/', 'Kblog.views.manage'),
	url(r'^manage_article/', 'Kblog.views.manage_article'),
	url(r'^manage_profile/', 'Kblog.views.manage_profile'),
	url(r'^manage_write/', 'Kblog.views.manage_write'),
	url(r'^manage_upload/', 'Kblog.views.manage_upload'),
	url(r'^manage_editarticle/', 'Kblog.views.manage_editarticle'),
	url(r'^manage_comment/', 'Kblog.views.manage_comment'),
	url(r'^manage_delcomment/', 'Kblog.views.manage_delcomment'),
	url(r'^manage_category/', 'Kblog.views.manage_category'),
	url(r'^manage_addcategory/', 'Kblog.views.manage_addcategory'),
	url(r'^manage_editcategory/', 'Kblog.views.manage_editcategory'),
	url(r'^manage_delcategory/', 'Kblog.views.manage_delcategory'),
	url(r'^manage_attachment/', 'Kblog.views.manage_attachment'),
	url(r'^manage_user/', 'Kblog.views.manage_user'),
	url(r'^manage_adduser/', 'Kblog.views.manage_adduser'),
	url(r'^manage_edituser/', 'Kblog.views.manage_edituser'),
	url(r'^manage_deluser/', 'Kblog.views.manage_deluser'),
	url(r'^manage_themes/', 'Kblog.views.manage_themes'),
	url(r'^manage_edittheme/', 'Kblog.views.manage_edittheme'),
	url(r'^manage_delattachment/', 'Kblog.views.manage_delattachment'),
	url(r'^manage_option/', 'Kblog.views.manage_option'),
	url(r'^manage_uptheme/', 'Kblog.views.manage_uptheme'),
	url(r'^manage_writefile/', 'Kblog.views.manage_writefile'),
    url(r'^test/', 'Kblog.views.test'),
)
