
import time

DAY_SECONDS = 86400

def day_start(timestamp):
    #TODO: support any timezone
    return timestamp - timestamp % DAY_SECONDS

def usertime(timestamp):
    #TODO: support user defined timezones
    return time.gmtime(timestamp)
