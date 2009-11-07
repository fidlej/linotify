
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

def send_payload(payload, url):
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

    except urllib2.HTTPError, e:
        if hasattr(e, 'read'):
            result = e.read()
            msg = '%s: %s' % (e, result)
        else:
            msg = str(e)
        raise Exception(msg)

