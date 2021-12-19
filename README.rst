****************
Mopidy-Listenbrainz
****************

.. image:: https://img.shields.io/pypi/v/Mopidy-Listenbrainz
    :target: https://pypi.org/project/Mopidy-Listenbrainz/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/workflow/status/suaviloquence/mopidy-listenbrainz/CI
    :target: https://github.com/suaviloquence/mopidy-listenbrainz/actions
    :alt: CI build status

.. image:: https://img.shields.io/codecov/c/gh/suaviloquence/mopidy-listenbrainz
    :target: https://codecov.io/gh/suaviloquence/mopidy-listenbrainz
    :alt: Test coverage

`Mopidy <https://www.mopidy.com/>`_ extension for 
`Listenbrainz <https://www.listenbrainz.org/>`_.

This extension requires a free user account at Listenbrainz.


Installation
============

Install by running::

    sudo python3 -m pip install Mopidy-Listenbrainz

See https://mopidy.com/ext/listenbrainz/ for alternative installation methods.


Configuration
=============

The extension is enabled by default when it is installed. You just need to add
your `Listenbrainz user token <https://listenbrainz.org/profile/>` to your Mopidy configuration file::

    [listenbrainz]
    token = 240420-249429-29449

The following configuration values are available:

- ``listenbrainz/enabled``: If the extension should be enabled or not.
  Defaults to enabled.
- ``listenbrainz/token``: Your `Listenbrainz user token <https://listenbrainz.org/profile/>`
- ``listenbrainz/url``: The URL of the API of the Listenbrainz instance to record listens to (default: api.listenbrainz.org)


Project resources
=================

- `Source code <https://github.com/suaviloquence/mopidy-listenbrainz>`_
- `Issue tracker <https://github.com/suaviloquence/mopidy-listenbrainz/issues>`_
- `Changelog <https://github.com/suaviloquence/mopidy-listenbrainz/releases>`_


Credits
=======

- Fork of `Mopidy-Scrobbler <https://github.com/mopidy/mopidy-scrobbler>` by `Stein Magnus Jodal <https://github.com/jodal>`__
- Current maintainer: `suaviloquence <https://github.com/suaviloquence>`__
- `Contributors <https://github.com/suaviloquence/mopidy-listenbrainz/graphs/contributors>`_
