#!usr/bin/env python3
# -*- coding: utf-8 -*-

import orm
import asyncio
from models import User,Blog,Comment

# def test():
# 	yield from orm.create_pool(user='root',password='',db='awesome',loop='loop')

# 	u = User(name='Test',email='test@example.com',password='123456',image='about:blank')

# 	yield from u.save()
# for x in test():
# 	pass

loop = asyncio.get_event_loop()
async def test():
    #创建连接池,里面的host,port,user,password需要替换为自己数据库的信息
    await orm.create_pool(loop=loop,host='127.0.0.1', port=3306,user='root', password='',db='awesome')
    #没有设置默认值的一个都不能少
    u = User(name='Know', email='test@qq.com', passwd='666666', image='about:blank',id="1")
    await u.save()

#把协程丢到事件循环中执行
loop.run_until_complete(test())

