#！user/bin/env python3
# -*- coding: utf-8 -*-

# 执行程序

import re,time,json,logging,hashlib,base64,asyncio

from coroweb import get,post

from models import User,Comment,Blog,next_id
@get('/')
async def index(request):
	# users = await User.findAll()
	summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
	blogs = [
		Blog(id='1', name='Test Blog', summary=summary,created_at=time.time()-120),
		Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600 ),
		Blog(id='3', name='There')
	]
	
	
	return{
		'__template__':'test.html',
		'users':users
	}