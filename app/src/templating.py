
import logging
from mako.lookup import TemplateLookup
from google.appengine.api import users

from src import config, formatting

TEMPLATE_LOOKUP = TemplateLookup(directories=['templates/'],
        format_exceptions=config.DEBUG,
        filesystem_checks=config.DEBUG,
        input_encoding='utf-8',
        default_filters=['unicode_with_replace', 'h'],
        imports=['from src.formatting import unicode_with_replace'])

def render(template_name, **kw):
    user = users.get_current_user()
    template = TEMPLATE_LOOKUP.get_template(template_name)
    return template.render_unicode(formatting=formatting,
            user=user,
            **kw)

