
import logging
import urllib2
try:
    import json
except ImportError:
    import simplejson as json

HEADERS = {
        'User-Agent': 'linotify-agent'
        }

def send_data(payload, url):
    logging.info('Sending: %r', payload)
    data = json.dumps(payload)

    request = urllib2.Request(url, data, headers=HEADERS)
    response = urllib2.urlopen(request)
    response = response.read()
    if response != 'OK':
        raise ValueError('Unexpected postback response: %r' % response)

