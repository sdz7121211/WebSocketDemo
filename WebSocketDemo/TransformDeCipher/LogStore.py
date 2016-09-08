import os
import traceback

class LogStore(object):
    out_file = {}

    def __init__(self, filename, line):
        self._Logging(filename, line)

    @staticmethod
    def _Logging(filename, line):
        path = "/".join(filename.split("/")[:-1])
        if not os.path.exists(path):
            os.system("mkdir -p %s" % path)
        out = LogStore.out_file[filename] if LogStore.out_file.get(filename, None) else open(filename, 'w')
        LogStore.out_file.setdefault(filename, out)
        print >> out, line

    @staticmethod
    def finished():
        for filename in LogStore.out_file.keys():
            try:
                LogStore.out_file[filename].close()
                os.system("gzip -f %s" % filename)
            except:
                print traceback.print_exc()
            del LogStore.out_file[filename]
