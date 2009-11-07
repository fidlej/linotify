
import logging
from ConfigParser import RawConfigParser

def read_config(filename):
    parser = RawConfigParser()
    parser.optionxform = str
    parser.read(filename)
    items = parser.items('main')
    config = dict(items)
    logging.debug('Config: %s', config)
    return config

