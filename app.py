#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#导入内部类
import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

import orm
#加入middleware、jinja2和自注册支持
from jinja2 import Environment,FileSystemLoader
from aiohttp import web
from coroweb import add_routes,add_static
#定义网页内容
def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', headers={'content-type':'text/html'})

#创建路由
@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

#middleware处理
#日志记录logger
@asyncio.coroutine
def logger_factory(app,handler):
	@asyncio.coroutine
	def logger(request):
		#记录日志
		logging.info('request:%s %s' %(request.method,request.path))
		#继续处理请求
		return (yield from handler(request))
	return logger

#处理返回值request
@asyncio.coroutine
def response_factory(app,handler):
	@asyncio.coroutine
	def response(request):
		#结果
		r = yield from handler(request)
		if isinstance(r,web.Response(body=r)):
			return r
		if isinstance(r.bytes):
			resp = web.Response(body=r)
			resp.content_type = 'appliction/octet-stream'
			return resp
		if isinstance(r,str):
			resp = web.Response(body=r.encode('utf-8'))
			resp.content_type = 'text/html:charset=utf-8'
			return resr
		if isinstance(r.dict):
			...
	pass

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

