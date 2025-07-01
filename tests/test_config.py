import os
from contextlib import contextmanager

import pytest
from hypothesis import given
from hypothesis import strategies as st

from git_batch_pull import config


@contextmanager
def set_env(token, folder):
    old_token = os.environ.get("github_token")
    old_folder = os.environ.get("local_folder")
    os.environ["github_token"] = token
    os.environ["local_folder"] = folder
    try:
        yield
    finally:
        if old_token is not None:
            os.environ["github_token"] = old_token
        else:
            os.environ.pop("github_token", None)
        if old_folder is not None:
            os.environ["local_folder"] = old_folder
        else:
            os.environ.pop("local_folder", None)


def test_load_config_env(monkeypatch):
    monkeypatch.setenv("github_token", "token")
    monkeypatch.setenv("local_folder", "/tmp")
    token, folder, _, _ = config.load_config()
    assert token == "token"
    assert folder == "/tmp"


def test_invalid_token(monkeypatch):
    monkeypatch.setenv("github_token", "ghp_xxx")
    monkeypatch.setenv("local_folder", "/tmp")
    with pytest.raises(Exception):
        config.load_config()


def test_invalid_local_folder(monkeypatch):
    monkeypatch.setenv("github_token", "token")
    monkeypatch.setenv("local_folder", "not/abs/path")
    with pytest.raises(Exception):
        config.load_config()


@given(
    token=st.text(min_size=1, max_size=100).filter(lambda s: "\x00" not in s),
    folder=st.text(min_size=1, max_size=100).filter(lambda s: "\x00" not in s),
)
def test_config_property(token, folder):
    with set_env(token, folder):
        try:
            config.load_config()
        except Exception:
            pass
