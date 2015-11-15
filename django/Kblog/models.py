#coding:utf-8
from django.db import models
from datetime import *  
import time
from PIL import Image

class Meta:
	db_table = 'Kblog'

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    pid = models.IntegerField(11)
    path = models.CharField(max_length=255)

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    author = models.IntegerField(max_length=11)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null = True)
    article_pic = models.FileField(upload_to = './Kblog/static/upload/')
    look_count = models.IntegerField(max_length=11)
    comment_count = models.IntegerField(max_length=11)
    update_time = models.DateTimeField(default=datetime.now)
    create_time = models.DateTimeField(default=datetime.now)
    article_status = models.CharField(max_length=20)
    comment_status = models.CharField(max_length=20)
    created = models.CharField(max_length=9)

class User(models.Model):
	user_id = models.AutoField(primary_key=True)
	username = models.CharField(unique=True, max_length=30)
	password = models.CharField(max_length=128)
	email = models.EmailField()
	group = models.CharField(default='visitor', max_length=16)
	status = models.IntegerField(max_length=1)
	register_time = models.DateTimeField(default=datetime.now)

class Relation(models.Model):
	id = models.AutoField(primary_key=True)
	aid = models.IntegerField(max_length=10)
	cid = models.IntegerField(max_length=10)

class Comment(models.Model):
	comment_id = models.AutoField(primary_key=True)
	avatar = models.CharField(max_length=20)
	comment = models.CharField(max_length=200)
	agent = models.CharField(max_length=255)
	ip = models.IPAddressField()
	pid = models.IntegerField(max_length=10)
	user_id = models.IntegerField(max_length=10)
	article_id = models.IntegerField(max_length=10)
	nickname = models.CharField(max_length=15)
	#approved,waiting
	status = models.CharField(default='waiting', max_length=15)
	create_time = models.DateTimeField(default=datetime.now)

class Attachment(models.Model):
	attrch_id = models.AutoField(primary_key=True)
	user_id = models.IntegerField(max_length=10)
	original_name = models.CharField(max_length=50)
	type = models.CharField(max_length=10)
	size = models.CharField(max_length=20)
	savepath = models.CharField(max_length=255)
	savename = models.CharField(max_length=50)
	suffix = models.CharField(max_length=20)
	alt = models.CharField(max_length=50)
	remark = models.CharField(max_length=150)
	update_time = models.IntegerField(max_length=10)
	create_time = models.IntegerField(max_length=10)

class Options(models.Model):
    name = models.CharField(primary_key=True, unique=True, max_length=32)
    value = models.TextField(blank=True, null = True)
'''
    def __unicode__(self):
		return self.name

    def __str__(self):
        return "%s, %s, %s, %s" % (self.category_id, self.name, self.pid, self.path)
'''
