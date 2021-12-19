from unittest import mock

from mopidy_listenbrainz import Extension
from mopidy_listenbrainz import frontend as frontend_lib


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert "[listenbrainz]" in config
    assert "enabled = true" in config
    assert "token =" in config
    assert "url =" in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert "token" in schema
    assert "url" in schema


def test_setup():
    ext = Extension()
    registry = mock.Mock()

    ext.setup(registry)

    registry.add.assert_called_once_with(
        "frontend", frontend_lib.ListenbrainzFrontend
    )
