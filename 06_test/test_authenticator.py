import pytest
from authenticator import Authenticator
from unittest.mock import MagicMock

@pytest.fixture
def authenticator():
    auth = Authenticator()
    yield auth

def test_register(authenticator):
    authenticator.register("username", "password")
    assert authenticator.users == {"username": "password"}

def test_register_error(authenticator):
    authenticator.register("username", "password")
    with pytest.raises(ValueError, match="エラー: ユーザーは既に存在します。"):
        authenticator.register("username", "password2")

def test_login(authenticator):
    authenticator.register("username", "password")
    assert authenticator.login("username", "password") == "ログイン成功"

def test_login_error(authenticator):
    with pytest.raises(ValueError, match="エラー: ユーザー名またはパスワードが正しくありません。"):
        authenticator.login("username", "password")