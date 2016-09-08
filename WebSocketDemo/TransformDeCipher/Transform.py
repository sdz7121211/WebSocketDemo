# coding: utf-8
# coding: utf-8
from Decipher import Decipher
import json
import urllib
import re
from TransformRule import TransformRule

class Transform(object):

    def __init__(self):
        self.decipher = Decipher()
        self.params_format = re.compile(ur"\[.*]")
        self.rule = TransformRule()

    def transform(self, line):
        items = line.split(",")
        ip = items[0]
        response_ty = items[3]
        assert "post" in response_ty.lower(), 'isnot POST REQUEST'
        content = items[4]
        if "&params=" in content:
            p1, p2 = content.split("&")
            tipkey = p1.split("=")[1].strip()
            params_enauth = p2.split("=")[1].strip()
            params = self._authLog(tipkey, params_enauth)
            auth_sw = 'on'
        else:
            params = urllib.unquote_plus(content.split("=")[1]).decode("utf8")
            auth_sw = 'off'
        for item in self.params_format.findall(params):
            params = item
            break
        for item in json.loads(params):
            item['auth'] = auth_sw
            item['ip'] = ip
            yield self.rule.applyRule(item)

    def _authLog(self, tipkey, params):
        dtipkey = self.decipher.deCiphering(tipkey)
        dparams = self.decipher.deCiphering(params, dtipkey)
        return dparams




if __name__ == "__main__":
    tester_Transform = Transform()
    line = '''183.232.175.3 - - [31/May/2016:06:20:26 +0800] "POST /appsta.js HTTP/1.1" 200 params=%5B%7B%22datatype%22%3A%2211FFE127604782539208DA065113107D%22%2C%22os%22%3A%22Android+4.2.2%22%2C%22pb%22%3A%22Wandoujia%22%2C%22pushid%22%3A%22UISEN127604D802F9208DA065IJ9E7SE%22%2C%22session%22%3A%7B%22eventId%22%3A%22null%22%2C%22interval%22%3A%22null%22%2C%22map%22%3Anull%2C%22netType%22%3A%22WIFI%22%2C%22opTime%22%3A%222016-01-29+03%3A04%3A01%22%2C%22opType%22%3A%22in%22%2C%22pageName%22%3A%22null%22%7D%2C%22ua%22%3A%22virtual+machine%22%2C%22userkey%22%3A%2263abd784f639ff7%22%2C%22vr%22%3A%221.0%22%7D%5D 18 "-" "Dalvik/1.6.0 (Linux; U; Android 4.2.2; virtual machine Build/JDQ39E)" -'''
    line = '''124.65.163.106 - - [29/May/2016:17:42:49 +0800] "POST /appsta.js HTTP/1.1" 200 abc=0dbTrX6a8BPWG0GhQyg6ag%3D%3D&params=Oh%2Fs7tw54Q6rwbTEA2LxUzA1%2Fj%2BL%2FzFaioODg0qYX5LJRtLH%2FfvfNtgj52T1+jpD%2BIcs0hydn1tHnE4MbHdqwwdHAzoklhOvAT9SW6DI5QRFPXA9xUwtV15Pw+6%2BN27PeDM9L9tOhZ%2Bj%2FKVN52wUxp7Idqj0UesuIdNfp8CvpJ6%2BjHidv3iKI4+L%2BU4bxqkW39HzmZgX96WG3oBVZavKWlMfjS6%2FY2gEQ%2F3TXto%2BVwnCGEiY%2Fzd+WB5TtFK7U8xHC%2BwJGXik%2FTTIesOgvLDFVxdjaaf4l%2Bs%2Bthwq251SuT6T%2FIXu+dk2%2FYp5Ckmw0aRLZnENk7M6m6dsepCKWf0Mz3vZNUosMLnOi6vaI5%2FxXd2jQ+%2BvIqM2DjdcQAwM7G39zxHxqcv7rvz4poFvmFgsA4dHz4xuuc814bCOl%2F6dGT+f%2BlwCDt3CoSRZbGyBC7Kc4guraBuNJ1Bs30LDlGH8QRDj%2B%2BUdT3YLe3DiI2P+poZXguZU02rE%2Bm7LEnaMq1br1WYzXR5DCtWYr4dSB2SYnxhSh9wddDPydBhB+bmYjhp%2FSlswuk0YpqVt8RwyU%2FtJyy9JA8Mbdjm6h4PQjbJ%2Bx9IUfmSVPGzSp+bqMNppEYrvWA4HIY%2BwB1BuuGlm%2BSFj%2B44vA2eUKrg4n1roFryfKFjYBfmvVN+3q3dART4qIinfErlIUKjGW8JXO9QHPv27laFHYelFWsPIWe9sHWmuNpfKJQH+SR9xdhxQJBiAH%2FpHrQmcaCrDJxzb5jsWZ6Qjgx05%2Fww4l4b%2FIkcILsbawQVN+Nk%2F%2FKQ%2BS2Pq5lVAX32eVlBYRWHV6QPLnYVHm87fu6LVYrurcxzUlDYSRR%2FYe+lK1RHOi6VBQ5D9hRNw%2FlL36vxq7FBfwU9vvLl6rtQ7HRgQb7JVEDPsRDx5nY+jhOJ8jNe82od7gl4kMtDmYKXxpvlJZbv05T0Pgp9vBLZGKnO%2B4l2Mprjy3Zb 18 "-" "Dalvik/1.6.0 (Linux; U; Android 4.4.4; Google Nexus 4 - 4.4.4 - API 19 - 768x1280 Build/KTU84P)" -'''
    line = '''124.65.163.106,-,[21/Aug/2016:16:55:38 +0800],"GET /appsta.js?params=JTdCJTIyYXBwa2V5JTIyJTNBJTIydGVzdGFwcCUyMiUyQyUyMnVyaSUyMiUzQSUyMmh0dHAlM0ElMkYlMkYxOTIuMTY4LjAuOTklM0E4MDgwJTJGSmluZ0hvbmclMkZhYm91dC5odG1sJTIyJTJDJTIycmVmJTIyJTNBJTIyaHR0cCUzQSUyRiUyRjE5Mi4xNjguMC45OSUzQTgwODAlMkZKaW5nSG9uZyUyRiUyMiUyQyUyMnNuYXBpZCUyMiUzQSUyMlBDJTJDd2luZG93c183JTJDQ01fNTAlMkMxOTIwKjEwODAlMjIlMkMlMjJkZXZpY2UlMjIlM0ElMjJQQyUyMiUyQyUyMnN5c3RlbSUyMiUzQSUyMndpbmRvd3NfNyUyMiUyQyUyMmJyb3dzZXIlMjIlM0ElMjJDTV81MCUyMiUyQyUyMnNjcmVlbiUyMiUzQSUyMjE5MjAqMTA4MCUyMiUyQyUyMnVpZCUyMiUzQSUyMjE0NzE3NjY5NjczNDZfNHhzdzhqNjg0OCUyMiUyQyUyMnRzJTIyJTNBMTQ3MTc2OTczODcyMyUyQyUyMnZyJTIyJTNBJTIyMS4xLjIlMjIlMkMlMjJzdXBwb3J0JTIyJTNBJTIyMDMlMjIlMkMlMjJ0eXBlJTIyJTNBJTIycGFnZSUyMiU3RA== HTTP/1.1",-,200 18,"-","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36" "-"'''
    # line = '''124.65.163.106,-,[22/Aug/2016:11:30:59 +0800],"POST /appsta.js HTTP/1.1",abc=7sFr5kL0OSImTtj4B%2Fo%2BsQ%3D%3D&params=s4nCmj%2FI3FQWE%2Bj1SahPjy%2B0wMJ1LxBexf1ndF8wVSvD3pQumEWaPAidlSwS+zzIaXF4TF0%2BZ8qyuRxbxkf3%2FlhiSgCnB6cy04IHs48IK9f7uerN0YM9lwddB+Z%2F0OXM55qhMSum4qGeupJzKK6J6NH0a5l6Ox8tq135vGnjjfhFxhw8fxt8cr+0Te5AlTvWzJk7%2F7zn4cWWLOPw1kkzRRBAI%2FDQdDytZe8IJAetYBEp%2F4oZepx+aNdiC39ERkS5LPxJUpxrekKf4OB1qNE0ZHUeKDmjVqfeyMShzkgfNSQ4D5p2+MdxOGgsNcmsuG5v%2FgqljblB5Qqb1Q4eyGBhPagyd%2B5bjjveknKg2En8Hq3hN+QSVdgb0a5iykXJMooKTOjWYR%2F3%2BrB6D4sR8lQZ1UEWvPp5DwOi4tXvFIjQmH+SKr6y2a9moFABwQt8kBlypqYQoNFM4aN18Jy1FPKqjoJznGwx8DIN%2F6vG5QQ+Wd1tZwkxFWc%3D,200 18,"-","Dalvik/2.1.0 (Linux; U; Android 5.1.1; Lenovo K32c36 Build/LMY47V)" "-"'''
    for item in tester_Transform.transform(line):
        print "eeeee", item
