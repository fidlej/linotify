"""
Functions to prevent a cross-site request forgery.
http://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)
"""

from waddon.handling import HttpError, set_cookie

def _check_csrf_cookie(request):
    token = request.get('_csrf')
    if not token:
        raise HttpError(403, 'A _csrf token is required.')
    if _get_csrf_cookie(request) != token:
        raise HttpError(403, 'A _csrf token is required.')

def _get_csrf_cookie(request):
    return request.cookies.get('_csrf')

def ensure_csrf_token(web_handler):
    """Ensures that a csrf cookie is set for the user.
    It returns the value of the cookie.
    """
    token = _get_csrf_cookie(web_handler.request)
    if not token:
        import binascii, uuid
        token = binascii.b2a_hex(uuid.uuid4().bytes)

    # The cookie expiration date is postponed by every request.
    set_cookie(web_handler.response, '_csrf', token, max_age_days=30)
    return token

def prevent_csrf(method):
    """A decorator to prevent CSRF before the function calls.
    Use it on post() methods.
    """
    def wrapper(self, *args, **kw):
        _check_csrf_cookie(self.request)
        return method(self, *args, **kw)

    return wrapper

