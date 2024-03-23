import datetime
import logging
from typing import cast, List
from uuid import uuid4

from mopidy.backend import Backend, PlaylistsProvider
from mopidy.models import Playlist, Ref
from mopidy.types import Uri, UriScheme


logger = logging.getLogger(__name__)


class ListenbrainzPlaylistsProvider(PlaylistsProvider):
    """Provider for ListenBrainz playlists.

    Note that this provider doesn't serialize the playlists. They're
    expected to be created by the frontend on each extension setup.

    This provider handles URIs with scheme ``listenbrainz:playlist``.

    """

    uri_prefix: UriScheme
    playlists: List[Playlist]

    def __init__(self, backend: Backend) -> None:
        super().__init__(backend)

        assert len(backend.uri_schemes) == 1
        self.uri_prefix = cast(UriScheme, backend.uri_schemes[0] + ":playlist")
        self.playlists = []

    def as_list(self) -> List[Ref]:
        return [Ref.playlist(uri=p.uri, name=p.name) for p in self.playlists]

    def create(self, name: str) -> Playlist | None:
        uri = f"{self.uri_prefix}:{uuid4()}"
        playlist = Playlist(uri=uri)
        self.playlists.append(playlist)
        return playlist

    def delete(self, uri: Uri) -> bool:
        return False

    def get_items(self, uri: Uri) -> List[Ref] | None:
        if not uri.startswith(self.uri_prefix):
            return None

        found = [p for p in self.playlists if p.uri == uri]
        if len(found) == 0:
            return None

        return [Ref.playlist(uri=p.uri, name=p.name) for p in found]

    def lookup(self, uri: Uri) -> Playlist | None:
        if not uri.startswith(self.uri_prefix):
            return None

        found = [p for p in self.playlists if p.uri == uri]
        if len(found) == 0:
            return None

        return found[0]

    def refresh(self) -> None:
        pass

    def save(self, playlist: Playlist) -> Playlist | None:
        uri = playlist.uri

        if not uri.startswith(self.uri_prefix):
            return None

        found = [p for p in self.playlists if p.uri == uri]
        if len(found) == 0:
            return None

        if len(found[0].tracks) > 0:
            return None  #  Playlists are expected to be saved
            #  once, by the frontend

        found[0] = playlist
        return found[0]
