
from src import store

def test_generate_server_secret():
    assert len(store._generate_server_secret(3)) == 3
    assert len(store._generate_server_secret(10)) == 10
    secret1 = store._generate_server_secret(10)
    secret2 = store._generate_server_secret(10)
    assert secret1 != secret2

