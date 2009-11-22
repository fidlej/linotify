
import time
from src.tz import usertime
from mako.filters import html_escape

def date_ys(timestamp, req):
    """Formats date with years up to seconds.
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', usertime(timestamp, req))

def date_ym(timestamp, req):
    """Formats date with years up to minutes.
    """
    return time.strftime('%Y-%m-%d %H:%M', usertime(timestamp, req))

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
    output = u''
    for key, value in map.iteritems():
        output += u' %s="%s"' % (html_escape(key), html_escape(value))
    return output

def select(option, actual_value):
    """Outputs class="selected" when the given option is selected.
    """
    if option == actual_value:
        return u'class="selected"'
    return u''

def select_option(option, actual_value):
    """Outputs selected="selected" when the given option is selected.
    """
    if option == actual_value:
        return u'selected="selected"'
    return u''

def offset(number):
    """Returns -number, +number or an empty string for zero.
    """
    if number == 0:
        return u''
    if number > 0:
        return u'+%s' % number
    return unicode(number)


