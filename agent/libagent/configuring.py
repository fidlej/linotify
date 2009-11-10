
import logging
from ConfigParser import RawConfigParser

DEFAULT_CONFIG = {
        'postbackUrl': 'http://www.linotify.com/postback',
        }

def read_config(filename):
    config = dict(DEFAULT_CONFIG)

    parser = RawConfigParser()
    parser.optionxform = str
    parser.read(filename)
    items = parser.items('main')
    config.update(items)
    logging.debug('Config: %s', config)
    return config

