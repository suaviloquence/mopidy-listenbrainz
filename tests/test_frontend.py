from unittest import mock

import pytest

from mopidy import models
from mopidy_listenbrainz import frontend as frontend_lib
from mopidy_listenbrainz.listenbrainz import Listenbrainz


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
