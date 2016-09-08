# coding: utf-8
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
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
# path = "C:/wstest.log"
fin = open(path)
filesize = os.path.getsize(path)


# 实时监控末尾是否有新数据到达，如果新数据到达则client返回对应数据，并把日志存入缓存，有新的链接优先返回缓存的数据
def freshCache():
    global path, fin, filesize
    for line in last_lines(fin, filesize, 10000):
        try:
            appengLog(line)
        except:
            import traceback
            print traceback.print_exc()
            print line
    for line in tail(fin):
        try:
            # print "read %d" % i
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
        isappend = False
        for clientid in clients.get(item["jhd_datatype"], {}).keys():
            try:
                for key in clients[item["jhd_datatype"]][clientid].rebackvalue:
                    if key == "jhd_opTime":
                        tmp.setdefault("jhd_opTime", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(time.strptime(item["jhd_opTime"].replace("-", "").replace(":", "").replace(" ", ""), "%Y%m%d%H%M%S")))))
                    else:
                        tmp.setdefault(key, item.get(key, None) if type(item.get(key, None)) != type({}) else json.dumps(item.get(key, None)))
                if not isappend:
                    logCache.setdefault(item["jhd_datatype"], []).append(tmp)
                    isappend = True
                logCache[item["jhd_datatype"]] = logCache.setdefault(item["jhd_datatype"], [])[-5:]
                clients[item["jhd_datatype"]][clientid].write_message(json.dumps(tmp, ensure_ascii=False))
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
        self.rebackvalue = ["jhd_userkey", "jhd_opType", "jhd_datatype", "jhd_map", "jhd_opTime", "jhd_eventId", "jhd_datatype"]
        self.appkey = None
        self.starttm = time.time()
        print "open", self._id, "clients number: %d" % sum([len(clients[appkey]) for appkey in clients])
        # print "open......"

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
    thread.start_new_thread(freshCache, ())
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(21333)
    tornado.ioloop.IOLoop.instance().start()
