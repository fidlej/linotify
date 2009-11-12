
from google.appengine.ext import webapp

class HttpError(Exception):
    def __init__(self, code, message):
        self.code = code
        Exception(self, message)

def handle_errors(web_handler, e, debug_mode):
    if isinstance(e, HttpError):
        web_handler.error(e.code)
        web_handler.response.write(str(e))

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
