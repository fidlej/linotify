#!/usr/bin/env python
"""\
Usage: %prog
Sends server statistics to a HTTP URL.
"""

import optparse
import logging

from libagent import measuring, sending, config

def _parse_args():
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
            help='increase verbosity')
    parser.add_option('-u', '--url',
            help='the destination URL (default=%s)' % config.POSTBACK_URL)
    parser.add_option('-n', '--dry-run', action='store_true',
            help="don't send anything")
    parser.set_defaults(verbosity=0, url=config.POSTBACK_URL)

    options, args = parser.parse_args()
    if len(args) != 0:
        parser.error('Extra arguments: %r' % args)

    return options

def _set_logging(verbosity):
    level = max(logging.DEBUG, logging.WARNING - 10*verbosity)
    logging.basicConfig(level=level)

def _prepare_payload(server_key, stats):
    return {
            'serverKey': server_key,
            'stats': stats,
            }

def main():
    options = _parse_args()
    _set_logging(options.verbosity)
    stats = measuring.measure_stats()
    payload = _prepare_payload(config.SERVER_KEY, stats)

    if not options.dry_run:
        sending.send_data(payload, options.url)
    else:
        import pprint
        pprint.pprint(payload)

if __name__ == '__main__':
    main()
