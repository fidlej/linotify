#!/usr/bin/env python
"""\
Usage: %prog
Sends server statistics to a HTTP URL.
"""

import optparse
import logging

from libagent import measuring, sending

def _parse_args():
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
            help='increase verbosity')
    parser.add_option('-n', '--dry-run', action='store_true',
            help="don't send anything")
    parser.set_defaults(verbosity=0)

    options, args = parser.parse_args()
    if len(args) != 0:
        parser.error('Extra arguments: %r' % args)

    return options

def _set_logging(verbosity):
    level = max(logging.DEBUG, logging.WARNING - 10*verbosity)
    logging.basicConfig(level=level)

def main():
    options = _parse_args()
    _set_logging(options.verbosity)
    stats = measuring.measure_stats()
    if not options.dry_run:
        sending.send_stats(stats)
    else:
        import pprint
        pprint.pprint(stats)

if __name__ == '__main__':
    main()
