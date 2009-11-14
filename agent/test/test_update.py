
from nose.tools import assert_equal
import update

def test_get_sha1sum():
    assert_equal(update._get_sha1sum('simplejson/encoder.py'),
            'fd82f84d590ffd29ea83f4897c620b11024af01b')

def test_read_chksums():
    chksums = update._read_chksums('test/files.sha1')
    assert_equal(len(chksums), 12)
    chksum, filename = chksums[1]
    assert_equal(chksum, '6696c5799acd390273eaa8ebe1bc35eaa938cc51')
    assert_equal(filename, 'simplejson/tool.py')
