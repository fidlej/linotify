
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
    """Sends the data to the given URL.
    It returns the state of the agent. A False return value suggests
    to do a agent update.
    """
    logging.info('Sending: %r', payload)
    data = {'payload': json.dumps(payload)}
    data = urllib.urlencode(data)

    request = urllib2.Request(url, data, headers=HEADERS)
    try:
        response = urllib2.urlopen(request)
        result = response.read()
    except urllib2.URLError, e:
        _handle_exception(e, ignore_site_errors)
        return False

    if result == 'OK':
        logging.debug('Success')
        agentok = True
    elif result.startswith('newer agent available'):
        logging.warning('Detected newer version: %s', result)
        agentok = False
    else:
        logging.warning('Unexpected postback response: %r', result)
        agentok = False

    return agentok


def _handle_exception(e, ignore_site_errors):
    """Ignores the website errors.
    Only HTTP code 404 isn't ignored. It could report the invalid serverKey.
    """
    if isinstance(e, urllib2.HTTPError):
        if hasattr(e, 'read'):
            result = e.read()
            msg = '%s: %s' % (e, result)
        else:
            msg = str(e)

        if e.code == 404:
            raise Exception(msg)
    else:
        msg = str(e)

    if ignore_site_errors:
        logging.info('Sending error: %s', msg)
    else:
        raise e

