#-*- coding: utf-8 -*-
#Created by Hans on 16-5-22

from tornado.web import Application
from tornado.options import options,define
from kazoo.client import KazooClient


define('port',default=8000,type=int,help='Server port')
define('bind',default='0.0.0.0',type=str,help='Server bind')

define('connect',default='127.0.0.1:2181',type=str,help='zookeeper connect')
define('root',default='/conf',type=str,help='zookeeper root')


def make_app(router,**settings):
    app = Application(router,**settings)
    zk = KazooClient(hosts=options.connect)
    setattr(app,'zk',zk)
    setattr(app,'options',options)

    return app