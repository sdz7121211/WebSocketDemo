# coding: utf-8
from Transform import Transform
import time
import sys
from LogStore import LogStore
import json

src_file_format = "/data1/nginxlogs/jhsaaslogs/access_jhlogs.%(yyyymmddhhmm)s"
errlog_path_format = "/data1/logs/transformsaaslog/err/%(yyyymmdd)s/%(hhmm)s.err"
filename_format = "/data1/logs/transformsaaslog/%(datatype)s/%(yyyymmdd)s/%(hhmm)s.log"


def main(timestamp, src_file_format=src_file_format):
    transform = Transform()
    yyyymmdd = time.strftime('%Y%m%d', time.localtime(timestamp))
    yyyymmddhhmm = time.strftime('%Y%m%d%H%M', time.localtime(timestamp))
    hhmm = time.strftime('%H%M', time.localtime(timestamp))
    src_file = src_file_format % {"yyyymmdd": yyyymmdd, "yyyymmddhhmm": yyyymmddhhmm}
    errlog_path = errlog_path_format % {"yyyymmdd": yyyymmdd, "hhmm": hhmm}
    with open(src_file) as f:
        for line in f:
            try:
                for item in transform.transform(line):
                    datatype = item['jhd_datatype']
                    filename = filename_format % {"yyyymmdd": yyyymmdd, "hhmm": hhmm, 'datatype': datatype}
                    line_out = json.dumps(item, ensure_ascii=False)
                    LogStore(filename, line_out)
            except Exception, e:
                LogStore(errlog_path, "%s, %s"%(e, line))
    LogStore.finished()

if __name__ == "__main__":
    if 'normal' in sys.argv:
        timestamp = int(time.time()-60*5)
        main(timestamp)

    if 'store' in sys.argv:
        # startstamp = time.mktime(time.strptime('20160501+000100', '%Y%m%d+%H%M%S'))
        # endstamp = time.mktime(time.strptime('20160602+000000', '%Y%m%d+%H%M%S'))
        startstamp = time.mktime(time.strptime('20160812+000000', '%Y%m%d+%H%M%S'))
        # startstamp = time.mktime(time.strptime('20160808+000000', '%Y%m%d+%H%M%S'))
        endstamp = time.mktime(time.strptime('20160812+103000', '%Y%m%d+%H%M%S'))
        while startstamp <= endstamp:
            # main(endstamp, src_logpath_format = "/data1/nginxlogs/jhlogs/%(yyyymmdd)s/access_jhlogs.%(yyyymmddhhmm)s.gz")
            try:
                # main(endstamp, src_logpath_format = "/data1/nginxlogs/guagua/%(yyyymmdd)s/access_guagua.%(yyyymmddhhmm)s.gz")
                main(endstamp, src_file_format = "/data1/nginxlogs/jhsaaslogs/access_jhlogs.%(yyyymmddhhmm)s")
            except:
                import traceback
                print traceback.print_exc()
            endstamp -= 60

