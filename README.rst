*******************
Mopidy-Listenbrainz
*******************

.. image:: https://img.shields.io/pypi/v/Mopidy-Listenbrainz
    :target: https://pypi.org/project/Mopidy-Listenbrainz/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/actions/workflow/status/suaviloquence/mopidy-listenbrainz/ci.yml
    :target: https://github.com/suaviloquence/mopidy-listenbrainz/actions
    :alt: CI build status

`Mopidy <https://www.mopidy.com/>`_ extension for 
`ListenBrainz <https://www.listenbrainz.org/>`_.

This extension requires a free user account at ListenBrainz.


Installation
============

Install by running::

    sudo python3 -m pip install Mopidy-Listenbrainz

See https://mopidy.com/ext/listenbrainz/ for alternative installation methods.


Configuration
=============

The extension is enabled by default when it is installed. You just need to add
your `ListenBrainz user token <https://listenbrainz.org/profile/>`_ to your Mopidy configuration file::

    [listenbrainz]
    token = 240420-249429-29449

The following configuration values are available:

- ``listenbrainz/enabled``: If the extension should be enabled or not.
  Defaults to enabled.
- ``listenbrainz/token``: Your `ListenBrainz user token <https://listenbrainz.org/profile/>`_
- ``listenbrainz/url``: The URL of the API of the ListenBrainz instance to record listens to (default: api.listenbrainz.org)
- ``listenbrainz/import_playlists``: Whether to import ListenBrainz playlists (default: ``false``)
- ``listenbrainz/search_schemes``: If non empty, the search for tracks in Mopidy's library is limited to results with the given schemes. The default value is ``"local:"`` to search tracks in Mopidy-Local library. It's recommended to customize the value according to your favorite backend but beware that not all backends support the required track search by ``musicbrainz_trackid`` (Mopidy-File, Mopidy-InternetArchive, Mopidy-Podcast, Mopidy-Somafm, Mopidy-Stream don't support such searches).
- ``search_schemes_fallback`` - A list of URI prefixes (e.g., ``local:``) to use to search by artist + track name when importing recommendation playlists, as a fallback when a track isn't found in the library by MusicBrainz ID. If empty, searches all URI prefixes, but make sure that an added URI should support searching and won't be rate-limited when importing many tracks at once.

Project resources
=================

- `Source code <https://github.com/suaviloquence/mopidy-listenbrainz>`_
- `Issue tracker <https://github.com/suaviloquence/mopidy-listenbrainz/issues>`_
- `Changelog <https://github.com/suaviloquence/mopidy-listenbrainz/releases>`_


Credits
=======

- Fork of `Mopidy-Scrobbler <https://github.com/mopidy/mopidy-scrobbler>`__ by `Stein Magnus Jodal <https://github.com/jodal>`__
- Current maintainer: `suaviloquence <https://github.com/suaviloquence>`__
- Playlist support by `Matthias Meulien <https://github.com/orontee>`__
- `Contributors <https://github.com/suaviloquence/mopidy-listenbrainz/graphs/contributors>`_
