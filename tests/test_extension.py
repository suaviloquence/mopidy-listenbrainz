from unittest import mock

from mopidy_listenbrainz import Extension
from mopidy_listenbrainz import frontend as frontend_lib, backend as backend_lib


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert "[listenbrainz]" in config
    assert "enabled = true" in config
    assert "token =" in config
    assert "url =" in config
    assert "import_playlists = false" in config
    assert "search_schemes = local:" in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert "token" in schema
    assert "url" in schema
    assert "import_playlists" in schema
    assert "search_schemes" in schema


def test_setup():
    ext = Extension()
    registry = mock.Mock()

    ext.setup(registry)

    registry.add.assert_any_call(
        "frontend",
        frontend_lib.ListenbrainzFrontend,
    )

    registry.add.assert_any_call(
        "backend",
        backend_lib.ListenbrainzBackend,
    )
