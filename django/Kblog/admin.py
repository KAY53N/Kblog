#!/usr/bin/python
# coding:utf-8
from django.contrib import admin
from Kblog.models import Article
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'website')  #设置作者类显示的表头
    search_fields = ('name',)                    #添加按姓名查询的功能
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('article_id', 'title', 'content')
admin.site.register(Article, ArticleAdmin)
