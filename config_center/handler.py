#-*- coding: utf-8 -*-
#Created by Hans on 16-5-22

import time
import os
from os import path as os_path
from tornado.web import RequestHandler
from tornado.options import options
from tornado.web import HTTPError
from kazoo.exceptions import NodeExistsError

class ConfHandler(RequestHandler):
    @staticmethod
    def persistence_conf(filename,content):
        os.makedirs(os.path.dirname(filename))
        with open(filename,'w') as f:
            f.write(content)


    def write_history(self,node,version):
        self.application.zk.ensure_path(os_path.join(node,'history'))
        try:
            node = os_path.join(node,'history')
            self.application.zk.create(os_path.join(node,version),b'')
        except NodeExistsError:
            raise HTTPError(500,reason='{0} is already exist !')
        except Exception as e:
            raise HTTPError(500,reason=str(e))

    def write_current(self,node,version):
        self.application.zk.ensure_path(os_path.join(node,'current'))
        try:
            node = os_path.join(node,'current')
            self.application.zk.create(os_path.join(node,'version'),version.encode())
        except NodeExistsError:
            self.application.zk.set(os_path.join(node,'version'),version.encode())
        except Exception as e:
            raise HTTPError(500,reason=str(e))

    def get(self):
        self.render('create.html')

    def post(self, *args, **kwargs):
        appid = self.get_argument('appid')
        conf_name = self.get_argument('conf_name')
        content = self.get_argument('content')

        #创建节点/conf/emnp/jdbc.properties
        node = os_path.join(options.root,appid,conf_name)
        self.application.zk.ensure_path(node)
        #创建子节点
        for line in content.split('\n'):
            n = line.split('=')
            k,v = n[0].strip(),n[1].strip()
            try:
                self.application.zk.create(os_path.join(node,k),v.encode())
            except NodeExistsError:
                #更新节点
                self.application.zk.set(os_path.join(node,k),v.encode())
            except Exception as e:
                raise HTTPError(500,reason=str(e))

        #持久化数据
        version = str(time.strftime("%Y%m%d%H%M%S",time.localtime(time.time())))
        file_path ='/'.join(['/tmp/workspace',options.root,appid,version,conf_name])
        ConfHandler.persistence_conf(file_path,content)
        #写history
        node = os_path.join(options.root,appid,'version')
        self.write_history(node,version)
        #写current
        self.write_current(node, version)
        #ConfHandler.write_current(version)
        self.write('create {0} success'.format(node))

class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')