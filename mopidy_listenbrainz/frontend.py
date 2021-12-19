import logging
import time

import pykka
from mopidy.core import CoreListener

from .listenbrainz import Listenbrainz

logger = logging.getLogger(__name__)


class ListenbrainzFrontend(pykka.ThreadingActor, CoreListener):
    lb: Listenbrainz

    def __init__(self, config, core):
        super().__init__()
        self.config = config

    def on_start(self):
        self.lb = Listenbrainz(
            self.config["listenbrainz"]["token"],
            self.config["listenbrainz"]["url"],
        )
        logger.debug("Listenbrainz token valid!")

    def track_playback_started(self, tl_track):
        track = tl_track.track
        artists = ", ".join(sorted([a.name for a in track.artists]))
        self.last_start_time = int(time.time())
        logger.debug(f"Now playing track: {artists} - {track.name}")

        self.lb.submit_listen(
            track=track.name or "",
            artist=artists,
            release=track.album and track.album.name or "",
            musicbrainz_id=track.musicbrainz_id or "",
            now_playing=True,
        )

    def track_playback_ended(self, tl_track, time_position):
        track = tl_track.track
        artists = ", ".join(sorted([a.name for a in track.artists]))
        duration = track.length and track.length // 1000 or 0
        time_position = time_position // 1000
        if duration < 30:
            logger.debug(f"Track too short to record. ({duration} < 30s)")
            return
        if time_position < duration // 2 and time_position < 240:
            logger.debug(
                "Track not played long enough to record. (50%% or 240s)"
            )
            return
        if self.last_start_time is None:
            self.last_start_time = int(time.time()) - duration
        logger.debug(f"Recording listen of track: {artists} - {track.name}")

        self.lb.submit_listen(
            track=track.name or "",
            artist=artists,
            release=track.album and track.album.name or "",
            musicbrainz_id=track.musicbrainz_id or "",
        )
