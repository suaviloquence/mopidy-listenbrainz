import time
from typing import Any, Dict

import requests

from . import __version__

SUBMIT_LISTEN_ENDPOINT = "/1/submit-listens"
VALIDATE_TOKEN_ENDPOINT = "/1/validate-token"


class Listenbrainz(object):
    token: str
    url: str

    def __init__(self, token: str, url: str) -> None:
        self.token = token
        self.url = url

        if not self.validate_token():
            raise RuntimeError(f"Token {token} is not valid")

    def validate_token(self) -> bool:
        response = requests.get(
            url=f"https://{self.url}{VALIDATE_TOKEN_ENDPOINT}",
            headers={
                "Authorization": f"Token {self.token}",
            },
        )

        if response.status_code != 200:
            return False

        return response.json()["valid"]

    def submit_listen(
        self,
        track: str,
        artist: str,
        release: str = "",
        musicbrainz_id: str = "",
        now_playing: bool = False,
    ) -> None:
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

        response = requests.post(
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