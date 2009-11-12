
import time
from src.tz import usertime
from mako.filters import html_escape

def date_ys(timestamp):
    """Formats date with years up to seconds.
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', usertime(timestamp))

def date_ym(timestamp):
    """Formats date with years up to minutes.
    """
    return time.strftime('%Y-%m-%d %H:%M', usertime(timestamp))

def point(value, precision):
    return '%.*f' % (precision, value)

def ago(seconds_ago):
    #TODO: switch to hours for big intervals
    minutes = seconds_ago // 60
    if minutes == 1:
        return '1 minute ago'
    else:
        return '%s minutes ago' % minutes

def attributes(map):
    output = ''
    for key, value in map.iteritems():
        output += ' %s="%s"' % (html_escape(key), html_escape(value))
    return output

