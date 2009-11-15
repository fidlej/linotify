#!/usr/bin/env python
"""\
Usage: update.py
Downloads and extracts the newest version of linotify-agent.
"""

import os
import os.path
import errno
import logging

# HTTPS URL is used to prevent a man-in-the-middle attack and data corruption
DOWNLOAD_URL = 'https://linotify-domain.appspot.com/static/download/linotify-agent.tar.gz'

# Confing files are not overwritten.
PRESERVED_FILES = ['config.cfg']

def _force_remove(path):
    """Removes the given path recursively (like rm -rf).
    It is OK if the path is already deleted.
    """
    import shutil
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

def _read_chksums(files_sha1sum_filename):
    """Returns a pair (chksum, path) for each file mentioned
    in the given filename.
    """
    chksums = []
    for line in open(files_sha1sum_filename):
        chksum, path = line.split()
        chksums.append((chksum, path))
    return chksums

def _update_files(agent_dir, fresh_dir):
    """Moves the files from the fresh_dir to agent_dir.
    The old extra files are then removed.
    """
    logging.info('Updating files in %s', agent_dir)
    osjoin = os.path.join
    old_chksums = _read_chksums(osjoin(agent_dir, 'files.sha1sum'))
    new_chksums = _read_chksums(osjoin(fresh_dir, 'files.sha1sum'))
    for chksum, filename in new_chksums:
        if filename in PRESERVED_FILES:
            continue

        install_path = osjoin(agent_dir, filename)
        old_chksum = _find_chksum(filename, old_chksums)
        if old_chksum:
            _backup_changed(install_path, old_chksum)
        os.rename(osjoin(fresh_dir, filename), install_path)

    used_filenames = [filename for ch, filename in new_chksums]
    _remove_unused(agent_dir, old_chksums, used_filenames)

def _find_chksum(filename, chksums):
    for chksum, name in chksums:
        if name == filename:
            return chksum
    return None

def _remove_unused(agent_dir, old_chksums, used_filenames):
    """Removes the old files that are not used any more.
    """
    for chksum, filename in old_chksums:
        if filename in used_filenames:
            continue

        path = os.path.join(agent_dir, filename)
        _backup_changed(path, chksum)
        os.unlink(path)

def _get_sha1sum(filename):
    """Returns sha1 hexdigest for the filename.
    It returns None when sha1 isn't provided by this Python version.
    """
    try:
        from hashlib import sha1
    except ImportError:
        return None

    m = sha1()
    m.update(open(filename).read())
    return m.hexdigest()

def _backup_changed(path, chksum):
    """Backups the file if its sha1sum differs from the given chksum.
    """
    try:
        actual_chksum = _get_sha1sum(path)
    except EnvironmentError, e:
        if e.errno == errno.ENOENT:
            # A missing old file is OK.
            return
        else:
            raise

    if actual_chksum and actual_chksum != chksum:
        logging.warn('File %s is changed locally. Making a .bak backup.', path)
        data = open(path).read()
        output = open(path + '.bak', 'wb')
        output.write(data)
        output.flush()
        os.fsync(output.fileno())
        output.close()

def main():
    logging.basicConfig(level=logging.INFO)
    agent_dir = os.path.dirname(os.path.realpath(__file__))
    update_dir = os.path.join(agent_dir, '.update')
    _force_remove(update_dir)

    tgz_stream = _stream(DOWNLOAD_URL)
    _extract(tgz_stream, update_dir)
    _update_files(agent_dir, os.path.join(update_dir, 'linotify-agent'))
    _force_remove(update_dir)

if __name__ == '__main__':
    main()

