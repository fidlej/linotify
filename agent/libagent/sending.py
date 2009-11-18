
import logging
import urllib2
import urllib
try:
    import json
except ImportError:
    import simplejson as json

HEADERS = {
        'User-Agent': 'linotify-agent',
        }

def send_payload(payload, url, ignore_site_errors=True):
    logging.info('Sending: %r', payload)
    data = {'payload': json.dumps(payload)}
    data = urllib.urlencode(data)

    request = urllib2.Request(url, data, headers=HEADERS)
    try:
        response = urllib2.urlopen(request)
        result = response.read()
        if result != 'OK':
            raise Exception('Unexpected postback response: %r' % result)
        else:
            logging.debug('Success')

    except urllib2.URLError, e:
        _handle_exception(e, ignore_site_errors)

def _handle_exception(e, ignore_site_errors):
    """Ignores the website errors.
    Only HTTP code 404 isn't ignored. It could report the invalid serverKey.
    """
    if isinstance(e, urllib2.HTTPError):
        if e.code == 404:
            if hasattr(e, 'read'):
                result = e.read()
                msg = '%s: %s' % (e, result)
            else:
                msg = str(e)
            raise Exception(msg)

    if ignore_site_errors:
        logging.info('Sending error: %s', e)
    else:
        raise e

