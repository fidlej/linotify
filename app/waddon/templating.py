
from mako.lookup import TemplateLookup

from waddon import config

TEMPLATE_LOOKUP = TemplateLookup(directories=[config.TEMPLATE_DIRECTORY],
        format_exceptions=config.DEBUG,
        filesystem_checks=config.DEBUG,
        input_encoding='utf-8',
        default_filters=['to_unicode', 'h'],
        imports=['from waddon.templating import to_unicode'])

def render(template_name, **kw):
    template = TEMPLATE_LOOKUP.get_template(template_name)
    return template.render_unicode(**kw)

def to_unicode(value):
    """Converts everything to unicode.
    Invalid utf-8 chars are replaced with question marks.
    """
    if isinstance(value, unicode):
        return value

    if not isinstance(value, str):
        value = str(value)
    return unicode(value, encoding='utf-8', errors='replace')

