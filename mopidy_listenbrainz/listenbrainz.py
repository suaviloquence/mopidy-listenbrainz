import datetime
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import pkg_resources
from mopidy import httpclient

import requests

from . import __version__

logger = logging.getLogger(__name__)

# Listenbrainz API
LIST_PLAYLIST_CREATED_FOR_ENDPOINT = "/1/user/{user}/playlists/createdfor"
PLAYLIST_ENDPOINT = "/1/playlist/{playlist_id}"
SUBMIT_LISTEN_ENDPOINT = "/1/submit-listens"
VALIDATE_TOKEN_ENDPOINT = "/1/validate-token"

# Musicbrainz resources
MUSICBRAINZ_PLAYLIST_EXTENSION_URL = "https://musicbrainz.org/doc/jspf#playlist"


@dataclass
class PlaylistData:
    playlist_id: str
    name: str
    track_mbids: List[str]
    last_modified: int


def playlist_identifier_to_id(playlist_identifier: str) -> Optional[str]:
    playlist_path = urlparse(playlist_identifier).path
    path_prefix = "/playlist/"
    return (
        playlist_path[len(path_prefix) :]
        if playlist_path.startswith(path_prefix)
        else None
    )


def track_identifier_to_mbid(track_identifier: str) -> Optional[str]:
    track_path = urlparse(track_identifier).path
    path_prefix = "/recording/"
    return (
        track_path[len(path_prefix) :]
        if track_path.startswith(path_prefix)
        else None
    )


def get_requests_session(proxy_config, user_agent):
    proxy = httpclient.format_proxy(proxy_config)
    full_user_agent = httpclient.format_user_agent(user_agent)

    session = requests.Session()
    session.proxies.update({"http": proxy, "https": proxy})
    session.headers.update({"user-agent": full_user_agent})

    return session


class _RequestError(Exception):
    pass


def check_response_status(response: requests.Response) -> None:
    if response.status_code == 200:
        return
    elif response.status_code == 400:
        logger.warning(f"Bad request {response.json()}")
    elif response.status_code == 401:
        logger.warning("Unauthorized request")
    elif response.status_code == 429:
        logger.warning("Too many requests")
    else:
        logger.warning(f"Unhandled status code {response.status_code}")

    raise _RequestError


class Listenbrainz(object):
    token: str
    url: str

    user_name: Optional[str]

    def __init__(self, token: str, url: str, proxy_config: Any) -> None:
        self.token = token
        self.url = url

        self.user_name = None  # initialized during token validation

        dist = pkg_resources.get_distribution("Mopidy-Listenbrainz")
        self.session = get_requests_session(
            proxy_config=proxy_config,
            user_agent=f"{dist.project_name}/{dist.version}",
        )

        if not self.validate_token():
            raise RuntimeError(f"Token {token} is not valid")

    def validate_token(self) -> bool:
        response = self.session.get(
            url=f"https://{self.url}{VALIDATE_TOKEN_ENDPOINT}",
            headers={
                "Authorization": f"Token {self.token}",
            },
        )

        try:
            check_response_status(response)
        except _RequestError:
            return False

        parsed_response = response.json()
        self.user_name = parsed_response.get("user_name")
        return parsed_response.get("valid")

    def submit_listen(
        self,
        track: str,
        artist: str,
        release: str = "",
        musicbrainz_id: str = "",
        now_playing: bool = False,
    ) -> None:
        if track == "" or artist == "":
            logger.debug("Won't submit listen for partially known track")
            return

        listen: Dict[str, Any] = {
            "track_metadata": {
                "track_name": track,
                "artist_name": artist,
                "release_name": release,
                "additional_info": {
                    "media_player": "Mopidy",
                    "submission_client": "Mopidy-Listenbrainz",
                    "submission_client_version": __version__,
                },
            },
        }

        if not now_playing:
            listen["listened_at"] = int(time.time())

        if musicbrainz_id:
            listen["track_metadata"]["additional_info"][
                "track_mbid"
            ] = musicbrainz_id

        payload = [listen]

        response = self.session.post(
            # hardcode https?
            url=f"https://{self.url}{SUBMIT_LISTEN_ENDPOINT}",
            json={
                "listen_type": "single" if not now_playing else "playing_now",
                "payload": payload,
            },
            headers={
                "Authorization": f"Token {self.token}",
            },
        )
        try:
            check_response_status(response)
        except _RequestError:
            pass

    def list_playlists_created_for_user(self) -> List[PlaylistData]:
        """List all playlist data from the "created for" endpoint.

        The "created for" endpoint list recommendation playlists; It
        is defined in ``LIST_PLAYLIST_CREATED_FOR_ENDPOINT``."""
        if self.user_name is None:
            logger.warning("No playlist created for unknown user!")
            return []

        path = LIST_PLAYLIST_CREATED_FOR_ENDPOINT.format(user=self.user_name)
        response = self.session.get(
            url=f"https://{self.url}{path}",
            headers={
                "Authorization": f"Token {self.token}",
            },
        )
        check_response_status(response)

        parsed_response = response.json()
        playlists: List[PlaylistData] = []
        found_playlists: List[str] = []
        for dto in parsed_response.get("playlists", []):
            playlist_dto = dto.get("playlist", {})
            playlist_identifier = playlist_dto.get("identifier")

            if playlist_identifier is None:
                logger.debug("Skipping playlist without identifier")
                continue

            if playlist_identifier in found_playlists:
                logger.warning(f"Duplicated playlist {playlist_identifier!r}")
                continue

            found_playlists.append(playlist_identifier)

            playlist_data = self._collect_playlist_data(playlist_identifier)
            if playlist_data is None:
                logger.warning(
                    f"Failed to build playlist {playlist_identifier!r}"
                )
                continue

            playlists.append(playlist_data)

        return playlists

    def _collect_playlist_data(
        self, playlist_identifier: str
    ) -> Optional[PlaylistData]:
        """Collect playlist data from a ListenBrainz playlist identifier.

        The ListenBrainz playlist identifier is a URL whose last path
        segment identifies the playlist. A playlist DTO is fetched
        from that identifier using ListenBrainz API.

        If the ListenBrainz playlist identifier doesn't match our
        expectations (see ``playlist_identifier_to_id()``), or the DTO
        hasn't the expected fields (``name``, ``date``), None is
        returned.

        MusicBrainz track identifiers are extracted from the tracks
        identifiers found in the DTO ``tracks`` field.

        """
        playlist_id = playlist_identifier_to_id(playlist_identifier)
        if playlist_id is None:
            logger.warning(
                f"Failed to extract playlist id from {playlist_identifier}"
            )
            return None

        path = PLAYLIST_ENDPOINT.format(playlist_id=playlist_id)
        response = self.session.get(
            url=f"https://{self.url}{path}",
            headers={
                "Authorization": f"Token {self.token}",
            },
        )
        try:
            check_response_status(response)
        except _RequestError:
            return None

        parsed_response = response.json()
        dto = parsed_response.get("playlist", {})
        name = dto.get("title")
        if name is None:
            logger.debug(f"Unable to read a name from playlist {playlist_id!r}")
            return None
        try:
            creation_date = datetime.datetime.fromisoformat(dto.get("date"))
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse date for playlist {playlist_id!r}")
            return None
        track_mbids = []
        for track_dto in dto.get("track", []):  # not tracks!
            track_identifiers: Union[str, list[str]] = track_dto.get(
                "identifier", {}
            )
            if isinstance(track_identifiers, str):
                track_identifiers = [track_identifiers]

            for track_identifier in track_identifiers:
                track_mbid = track_identifier_to_mbid(track_identifier)
                if track_mbid is None:
                    logger.debug(
                        f"Failed to identify MBID from {track_identifier!r}"
                    )
                    continue
                else:
                    track_mbids.append(track_mbid)
                    break

        if len(track_mbids) == 0:
            logger.debug(
                f"No MBID found for tracks of playlist {playlist_id!r}"
            )
            return None

        return PlaylistData(
            playlist_id, name, track_mbids, int(creation_date.timestamp())
        )
