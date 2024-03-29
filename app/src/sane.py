"""
A module to convert input values
into sane values.
"""

from google.appengine.api import users

def valid_name(value):
    if not value:
        value = 'noname'
    # App Engine datastore limits strings to 500 bytes
    return value[:251]

def valid_int(value, min_value=None):
    """Converts the value to an integer value.
    """
    try:
        result = int(value)
    except ValueError:
        result = 0

    if min_value is not None:
        result = max(min_value, result)
    return result

def valid_entity(model, id):
    from src import store
    id = valid_int(id)
    entity = model.get_by_id(id)

    user = users.get_current_user()
    if not entity or (
            entity.user_id != user.user_id()
            and not users.is_current_user_admin()):
        raise store.NotFoundError("No such %s entity: %r" % (model, id))

    return entity

def valid_chart(chart_index):
    from src import chartdef, store
    chart_index = valid_int(chart_index)
    if chart_index < 0 or chart_index >= len(chartdef.CHARTS):
        raise store.NotFoundError("Wrong chart index: %r" % chart_index)

    return chartdef.CHARTS[chart_index]


class RequestContext(object):
    def __init__(self, request):
        self.request = request

    def get_tzoffset_seconds(self):
        """Returns the timezone offset for the current user for today.
        """
        offset = self.request.cookies.get('tz', u'0')
        if offset.endswith('p'):
            offset = offset[:-1]

        return valid_int(offset)

