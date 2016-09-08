# coding: utf-8
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import ssl
# import time
# import glob
from multitail import multitail
from lastLines import last_lines
from TransformDeCipher import Transform
import traceback
import os
import json
from Tail import tail
import thread
from uuid import uuid4
import time

global transform
transform = Transform.Transform()

global logCache
logCache = {}

global clients
clients = {}

global path, fin, filesize

path = "/data1/nginxlogs/cjtest_logs/access.log"
fin = open(path)
filesize = os.path.getsize(path)


# 实时监控末尾是否有新数据到达，如果新数据到达则client返回对应数据，并把日志存入缓存，有新的链接优先返回缓存的数据
def freshCache():
    global path, fin, filesize
    for line in last_lines(fin, filesize, 1000):
        try:
            appengLog(line)
        except:
            import traceback
            print traceback.print_exc()
            print line
    for line in tail(fin):
        try:
            appengLog(line)
        except:
            import traceback
            print traceback.print_exc()
            print line

def appengLog(line):
    global logCache
    global clients
    for item in transform.transform(line):
        tmp = {}
        tmp.setdefault("jhd_userkey", item["jhd_userkey"])
        tmp.setdefault("jhd_opType", item["jhd_opType"])
        tmp.setdefault("jhd_datatype", item["jhd_datatype"])
        tmp.setdefault("jhd_map", item["jhd_map"])
        tmp.setdefault("jhd_opTime", item["jhd_opTime"])
        tmp.setdefault("jhd_eventId", item["jhd_eventId"])
        logCache.setdefault(item["jhd_datatype"], []).append(tmp)
        logCache[item["jhd_datatype"]] = logCache.setdefault(item["jhd_datatype"], [])[-5:]
        for clientid in clients.get(item["jhd_datatype"], {}).keys():
            try:
                clients[tmp["jhd_datatype"]][clientid].write_message(json.dumps(tmp, ensure_ascii=False))
            except:
                import traceback
                print traceback.print_exc()

# websocket 服务
class EchoWebSocket(tornado.websocket.WebSocketHandler):

    global clients

    def check_origin(self, origin):
        return True

    def open(self):
        self._id = uuid4()
        self.appkey = None
        self.starttm = time.time()
        print "open", self._id, "clients number: %d" % sum([len(clients[appkey]) for appkey in clients])

    def on_message(self, message):
        global logCache
        try:
            data = json.loads(message)
        except:
            feedback = {"info": "无效参数"}
            self.write_message(json.dumps(feedback, ensure_ascii=False))
        if "jhd_datatype" in data and "keys" in data:
            if self.appkey is None:
                self.appkey = data["jhd_datatype"]
                self.rebackvalue = data["keys"] if data["keys"] else self.keys
                clients.setdefault(self.appkey, {}).setdefault(self._id, self)
                logs = logCache.get(self.appkey, [])
                for pos in range(1, len(logs)+1):
                    index = len(logs) - pos
                    self.write_message(json.dumps(logs[index], ensure_ascii=False))
        else:
            feedback = {"info": "无效参数"}
            self.write_message(json.dumps(feedback, ensure_ascii=False))

    def on_close(self):
        if self.appkey:
            del clients[self.appkey][self._id]
        print "end:", self._id, ", connect continuse time: %d s" % int(time.time()-self.starttm), ", clients number: %d" % sum([len(clients[appkey]) for appkey in clients])


class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexPageHandler),
            (r'/websocket', EchoWebSocket)
        ]

        settings = {
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    from os import sys, path
    cur_path = path.dirname(path.abspath(__file__))
    # print path.dirname(path.dirname(path.abspath(__file__)))

    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(os.path.join(cur_path, "wssdata/*.crt"),
                            os.path.join(cur_path, "wssdata/*.key"))

    thread.start_new_thread(freshCache, ())
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app, ssl_options=ssl_ctx)
    server.listen(21333)
    tornado.ioloop.IOLoop.instance().start()
