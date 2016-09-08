import time
SLEEP_INTERVAL = 1.0

def tail(fin):
    "Listen for new lines added to file."
    i = 0
    while True:
        where = fin.tell()
        print "read %d" % i, "seek pos %d" % where
        line = fin.readline()
        if not line:
            time.sleep(SLEEP_INTERVAL)
            fin.seek(where)
        else:
            yield line
        i += 1

if __name__ == "__main__":
    path = "c:/wstest.log"
    f = open(path)
    for line in tail(f):
        print line