#!/usr/bin/env python
"""\
Usage: %prog
Sends server statistics to a HTTP URL.
"""

import os.path
import optparse
import logging

from libagent import measuring, sending, configuring

VERSION = '0.2.0'
CONFIG_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        'config.cfg')

def _parse_args():
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
            help='increase verbosity')
    parser.add_option('-c', '--config',
            help='use different config (default=%s)' % CONFIG_FILENAME)
    parser.add_option('-n', '--dry-run', action='store_true',
            help="don't send anything")
    parser.set_defaults(verbosity=0, config=CONFIG_FILENAME)

    options, args = parser.parse_args()
    if len(args) != 0:
        parser.error('Extra arguments: %r' % args)

    return options

def _set_logging(verbosity):
    level = max(logging.DEBUG, logging.WARNING - 10*verbosity)
    logging.basicConfig(level=level,
            format='%(levelname)s: %(message)s')

def _prepare_payload(server_key, stats):
    return {
            'version': VERSION,
            'serverKey': server_key,
            'stats': stats,
            }

def main():
    options = _parse_args()
    _set_logging(options.verbosity)
    config = configuring.read_config(options.config)
    stats = measuring.measure_stats()
    payload = _prepare_payload(config['serverKey'], stats)

    if options.dry_run:
        print 'payload:', payload
        return

    try:
        sending.send_payload(payload, config['postbackUrl'])
    except Exception, e:
        logging.error('Unable to send the stats: %s', e)

if __name__ == '__main__':
    main()
