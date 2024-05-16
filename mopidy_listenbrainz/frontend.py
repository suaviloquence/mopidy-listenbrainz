import logging
import time
from datetime import datetime, timedelta
from threading import Timer
from typing import List

import pykka
from mopidy.core import CoreListener
from mopidy.models import Playlist, Track

from .listenbrainz import Listenbrainz, PlaylistData

logger = logging.getLogger(__name__)


class ListenbrainzFrontend(pykka.ThreadingActor, CoreListener):
    lb: Listenbrainz

    def __init__(self, config, core):
        super().__init__()
        self.config = config
        self.library = core.library
        self.playlists = core.playlists
        self.playlists_update_timer = None

    def on_start(self):
        self.lb = Listenbrainz(
            self.config["listenbrainz"]["token"],
            self.config["listenbrainz"]["url"],
            self.config["proxy"],
        )
        logger.debug("Listenbrainz token valid!")

        if self.config["listenbrainz"].get("import_playlists", False):
            search_schemes = self.config["listenbrainz"].get(
                "search_schemes", ["local:"]
            )
            if len(search_schemes) > 0:
                logger.debug(
                    f"Will limit track searches to URIs: {search_schemes}"
                )
            else:
                msg = (
                    "Track searches among all backends aren't stable! "
                    "Better configure `search_schemes' to match your "
                    "favorite backend"
                )
                logger.warn(msg)

            self.import_playlists()

    def on_stop(self):
        if self.playlists_update_timer:
            self.playlists_update_timer.cancel()

    def import_playlists(self) -> None:
        logger.info("Importing ListenBrainz playlists")

        import_count = 0
        playlist_datas = self.lb.list_playlists_created_for_user()
        logger.debug(f"Found {len(playlist_datas)} playlists to import")

        existing_playlists = self.playlists.as_list().get()
        recommendation_playlist_uri_prefix = (
            "listenbrainz:playlist:recommendation"
        )
        filtered_existing_playlists = dict(
            [
                (ref.uri, ref)
                for ref in existing_playlists
                if ref.uri.startswith(recommendation_playlist_uri_prefix)
            ]
        )

        for playlist_data in playlist_datas:
            source = playlist_data.playlist_id
            playlist_uri = f"{recommendation_playlist_uri_prefix}:{playlist_data.playlist_id}"
            tracks = self._collect_playlist_tracks(playlist_data)

            if len(tracks) == 0:
                logger.debug(
                    f"Skipping import of playlist with no known track for {source!r}"
                )
                continue

            if playlist_uri in filtered_existing_playlists:
                filtered_existing_playlists.pop(playlist_uri)
                # must pop since filtered_existing_playlists will
                # finally be deleted

                logger.debug(f"Already known playlist {playlist_uri}")
                # maybe there're new tracks in Mopidy's database...
            else:
                query = self.playlists.create(
                    name=playlist_uri, uri_scheme="listenbrainz"
                )
                # Hack, hack: The backend uses first parameter as URI,
                # not name...
                playlist = query.get()
                if playlist is None:
                    logger.warning(f"Failed to create playlist for {source!r}")
                    continue

                logger.debug(f"Playlist {playlist.uri!r} created")

            complete_playlist = Playlist(
                uri=playlist_uri,
                name=playlist_data.name,
                tracks=tracks,
                last_modified=playlist_data.last_modified,
            )
            query = self.playlists.save(complete_playlist)
            playlist = query.get()
            if playlist is None:
                logger.warning(f"Failed to save playlist for {source!r}")
            else:
                import_count += 1
                logger.debug(
                    f"Playlist saved with {len(playlist.tracks)} tracks {playlist.uri!r}"
                )

        for playlist in filtered_existing_playlists.values():
            logger.debug(f"Deletion of obsolete playlist {playlist.uri!r}")
            self.playlists.delete(playlist.uri)

        logger.info(
            f"Successfully imported ListenBrainz playlists: {import_count}"
        )
        self._schedule_playlists_import()

    def _collect_playlist_tracks(
        self, playlist_data: PlaylistData
    ) -> List[Track]:
        tracks: List[Track] = []
        search_schemes = self.config["listenbrainz"].get(
            "search_schemes", ["local:"]
        )

        for track_mbid in playlist_data.track_mbids:
            query = self.library.search(
                {"musicbrainz_trackid": [track_mbid]}, uris=search_schemes
            )
            results = query.get()

            found_tracks = [t for r in results for t in r.tracks]
            if len(found_tracks) == 0:
                continue

            tracks.append(found_tracks[0])
        return tracks

    def _schedule_playlists_import(self):
        now = datetime.now()
        days_until_next_monday = 7 - now.weekday()
        timer_interval = timedelta(days=days_until_next_monday).total_seconds()
        logger.debug(f"Playlist update scheduled in {timer_interval} seconds")
        self.playlists_update_timer = Timer(
            timer_interval, self.import_playlists
        )
        self.playlists_update_timer.start()

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
