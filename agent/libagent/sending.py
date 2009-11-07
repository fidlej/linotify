
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
    response = urllib2.urlopen(request)
    response = response.read()
    if response != 'OK':
        raise ValueError('Unexpected postback response: %r' % response)
    else:
        logging.debug('Success')

