
from nose.tools import eq_ as eq
from nose.tools import assert_not_equal
from src import store

def test_generate_server_secret():
    eq(len(store._generate_server_secret(3)), 3)
    eq(len(store._generate_server_secret(10)), 10)
    secret1 = store._generate_server_secret(10)
    secret2 = store._generate_server_secret(10)
    assert_not_equal(secret1, secret2)

