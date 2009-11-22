
import time

DAY_SECONDS = 86400

def day_start(timestamp, req):
    start = timestamp - timestamp % DAY_SECONDS
    return start + req.get_tzoffset_seconds()

def usertime(timestamp, req):
    return time.gmtime(timestamp - req.get_tzoffset_seconds())

