
from nose.tools import assert_equal, assert_true
import update
import os
import os.path

def test_get_sha1sum():
    assert_equal(update._get_sha1sum('simplejson/encoder.py'),
            'fd82f84d590ffd29ea83f4897c620b11024af01b')

def test_read_chksums():
    chksums = update._read_chksums('test/files.sha1')
    assert_equal(len(chksums), 12)
    chksum, filename = chksums[1]
    assert_equal(chksum, '6696c5799acd390273eaa8ebe1bc35eaa938cc51')
    assert_equal(filename, 'simplejson/tool.py')

def test_backup_changed():
    path = 'test/test_update.py'
    backup_path = path + '.bak'
    if os.path.exists(backup_path):
        os.unlink(backup_path)
    update._backup_changed('test/test_update.py', 'my_chksum')
    assert_true(os.path.exists('test/test_update.py.bak'))
    os.unlink('test/test_update.py.bak')

def test_backup_missing():
    update._backup_changed('test/no_such_file', 'my_chksum')
    assert_true(not os.path.exists('test/test_update.py.bak'))
