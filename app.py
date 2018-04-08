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
from config import configs
from handlers import cookie2user, COOKIE_NAME

#定义jinja2
def init_jinja2(app,**kw):
	logging.info('init jinja2...')
	options = dict(
		autoescape = kw.get('autoescape',True),
		block_start_string = kw.get('block_start_string','{%'),
		block_end_string = kw.get('block_end_string','%}'),
		variable_start_string = kw.get('variable_start_string','{{'),
		variable_end_string = kw.get('variable_end_string','}}'),
		auto_reload = kw.get('auto_reload',True)
	)
	path = kw.get('path',None)
	if path is None:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
	logging.info('set jinja2 template path: %s' %path)
	env = Environment(loader=FileSystemLoader(path),**options)
	filters = kw.get('filters',None)
	if filters is not None:
		for name,f in filters.items():
			env.filters[name] = f
	app['__templating__'] = env

#middleware处理
#日志记录logger
async def logger_factory(app, handler):
    async def logger(request):
    	#记录日志
        logging.info('Request: %s %s' % (request.method, request.path))
        #继续处理请求
        # await asyncio.sleep(0.3)
        return (await handler(request))
    return logger

#绑定cookie
async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user.email)
                request.__user__ = user
        if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
            return web.HTTPFound('/signin')
        return (await handler(request))
    return auth
#data空间
async def data_factory(app,handler):
	async def parse_data(request):
		if request.content_type.startswith('appliction/json'):
			request.__data__ = await request.json()
			logging.info('request json: %s' %str(request.__data__))
		elif request.content_type.startswith('appliction/x-www-form-urlencoded'):
			request.__data__ = await request.post()
			logging.info('request from: %s' %str(request.__data__))
		return (await handler(request))
	return parse_data

#处理返回值request
async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                r['__user__'] = r.get('__user__')
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response

#定义时间处理函数
def datetime_filter(t):
	delta = int(time.time() - t)
	if delta < 60:
		return u'1分钟前'
	if  delta < 3600:
		return u'%s 分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s 小时前' % (delta // 3600)
	if delta <604800:
		return u'%s 天前' % (delta // 86400)
	dt = datetime.fromtimestamp(t)
	return u'%s 年 %s 月 %s 日' % (dt.year,dt.month,dt.day)

#定义网页内容
# def index(request):
#     return web.Response(body=b'<h1>Awesome</h1>', headers={'content-type':'text/html'})

#创建路由进程
# @asyncio.coroutine
# def init(loop):
#     app = web.Application(loop=loop)
#     app.router.add_route('GET', '/', index)
#     srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
#     logging.info('server started at http://127.0.0.1:9000...')
#     return srv

async def init(loop):
	await orm.create_pool(loop=loop,host='127.0.0.1',port=3306,user='root',password='',db='awesome')
	app = web.Application(loop=loop,middlewares=[
		logger_factory,response_factory
		])
	init_jinja2(app,filters=dict(datetime=datetime_filter))
	add_routes(app,'handlers')
	add_static(app)
	srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
	logging.info('server started at http://127.0.0.1:9000...')
	return srv
	
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

