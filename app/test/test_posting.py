
from nose.tools import eq_ as eq
from src import posting

def test_get_next_end():
    eq(posting._get_next_end(300, 300), 450)
    eq(posting._get_next_end(300, 320), 450)
    eq(posting._get_next_end(300, 450), 750)
    eq(posting._get_next_end(300, 480), 750)
