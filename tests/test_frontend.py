from unittest import mock

import pytest

from mopidy_listenbrainz import frontend as frontend_lib


@pytest.fixture
def frontend():
    config = {
        "listenbrainz": {
            "token": "xsjk",
        }
    }
    core = mock.sentinel.core
    return frontend_lib.ListenbrainzFrontend(config, core)


# TODO
