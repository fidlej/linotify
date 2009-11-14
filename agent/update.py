#!/usr/bin/env python
"""\
Usage: update.py
Downloads and extracts the newest version of linotify-agent.
"""

import os.path
import logging

# HTTPS URL is used to prevent a man-in-the-middle attack and data corruption
DOWNLOAD_URL = 'https://linotify-domain.appspot.com/static/download/linotify-agent.tar.gz'

def _force_remove(path):
    """Removes the given path recursively (like rm -rf).
    It is OK if the path is already deleted.
    """
    import shutil, errno
    try:
        shutil.rmtree(path)
    except OSError, e:
        if e.errno != errno.ENOENT:
            raise

def _stream(url):
    import urllib2
    logging.info('Downloading: %s', url)
    return urllib2.urlopen(url)

def _extract(tgz_stream, dest):
    import tarfile
    tar = tarfile.open(fileobj=tgz_stream, mode='r|*')
    tar.extractall(dest)

def main():
    logging.basicConfig(level=logging.INFO)
    agent_dir = os.path.dirname(os.path.realpath(__file__))
    update_dir = os.path.join(agent_dir, '.update')
    _force_remove(update_dir)

    tgz_stream = _stream(DOWNLOAD_URL)
    _extract(tgz_stream, update_dir)
    #TODO: move the files

if __name__ == '__main__':
    main()

