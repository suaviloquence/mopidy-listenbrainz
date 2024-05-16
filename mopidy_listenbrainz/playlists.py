import logging
from typing import cast, List, NewType

from mopidy.backend import Backend, PlaylistsProvider
from mopidy.models import Playlist, Ref

try:
    from mopidy.types import Uri, UriScheme
except ModuleNotFoundError:
    Uri = NewType("Uri", str)
    UriScheme = NewType("UriScheme", str)


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
        uri = name
        if not uri.startswith(self.uri_prefix):
            return None

        playlist = Playlist(uri=uri, name=name)
        self.playlists.append(playlist)
        return playlist

    def delete(self, uri: Uri) -> bool:
        if not uri.startswith(self.uri_prefix):
            return False

        found = [p for p in self.playlists if p.uri == uri]
        if len(found) == 0:
            return False

        pos = self.playlists.index(found[0])
        del self.playlists[pos]
        return True

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

        if uri.startswith(self.uri_prefix + ":recommendation"):
            if not (len(playlist.tracks) > len(found[0].tracks)):
                # return unchanged playlist for recommendations whose
                # track list isn't increasing, really save iff first
                # save after creation or new tracks being available in
                # Mopidy's database
                return found[0]

        pos = self.playlists.index(found[0])
        self.playlists[pos] = playlist
        return self.playlists[pos]
