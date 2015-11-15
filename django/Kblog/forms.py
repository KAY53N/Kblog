# -*- coding:utf-8 -*-
from django import forms
 
class SignupForm(forms.Form):
    username = forms.CharField(required=True, min_length=6, label='用户名')
    email = forms.EmailField(required=True, label='Email')
    upwd = forms.CharField(required=True, min_length=6, label='密码')
    repwd = forms.CharField(required=True, min_length=6, label='确认密码')
    code = forms.CharField(required=True, min_length=4, label='验证码')
class SigninForm(forms.Form):
    username = forms.CharField(required=True, min_length=6, label='用户名')
    upwd = forms.CharField(required=True, min_length=6, label='密码')
class CommentForm(forms.Form):
    nickname = forms.CharField(required=True, min_length=2, label='昵称')
    comment = forms.CharField(required=True, min_length=5, label='评论内容')
