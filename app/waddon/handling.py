
import logging
from google.appengine.ext import webapp

class HttpError(Exception):
    def __init__(self, code, message):
        self.code = code
        Exception.__init__(self, message)

    def __str__(self):
        return '%s: %s' % (self.code, self.message)

def show(web_handler, output):
    web_handler.response.out.write(output)

def handle_errors(web_handler, e, debug_mode):
    if isinstance(e, HttpError):
        logging.info('HTTP error: %s', e)
        web_handler.error(e.code)
        show(web_handler, str(e))
        return

    webapp.RequestHandler.handle_exception(web_handler, e, debug_mode)

def set_cookie(response, key, value='', max_age_days=0, path='/'):
    from Cookie import BaseCookie
    cookies = BaseCookie()
    cookies[key] = value
    morsel = cookies[key]
    morsel['max-age'] = max_age_days * 86400
    morsel['path'] = path

    output = morsel.output(header='')
    response.headers.add_header('Set-Cookie', output)

