"""
Unit tests for plugin discovery in git_batch_pull.plugins.
Covers successful and failed plugin loading via entry points.
"""

import importlib

from git_batch_pull.plugins import discover_plugins


class DummyEntryPoint:
    """
    Dummy entry point for simulating plugin discovery and loading.
    """

    def __init__(self, name, module, should_fail=False):
        self.name = name
        self.module = module
        self.should_fail = should_fail

    def load(self):
        """
        Simulate loading a plugin, optionally raising an exception.
        """
        if self.should_fail:
            raise Exception("Failed to load plugin!")
        return f"plugin-{self.name}"


def test_discover_plugins_success(monkeypatch):
    """
    Test that discover_plugins returns successfully loaded plugins.
    """
    monkeypatch.setattr(
        importlib.metadata,
        "entry_points",
        lambda: {"git_batch_pull_plugins": [DummyEntryPoint("foo", "foo_mod")]},
    )
    found = discover_plugins()
    assert "foo" in found
    assert found["foo"] == "plugin-foo"


def test_discover_plugins_failure(monkeypatch):
    """
    Test that discover_plugins returns empty dict when plugin loading fails.
    """
    monkeypatch.setattr(
        importlib.metadata,
        "entry_points",
        lambda: {"git_batch_pull_plugins": [DummyEntryPoint("bar", "bar_mod", should_fail=True)]},
    )
    found = discover_plugins()
    assert found == {}
