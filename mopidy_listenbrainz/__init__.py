import pathlib

import pkg_resources
from mopidy import config, ext

__version__ = pkg_resources.get_distribution("Mopidy-Listenbrainz").version


class Extension(ext.Extension):

    dist_name = "Mopidy-Listenbrainz"
    ext_name = "listenbrainz"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["token"] = config.Secret()
        schema["url"] = config.String()
        schema["import_playlists"] = config.Boolean()
        schema["search_schemes"] = config.List(optional=True)
        return schema

    def setup(self, registry):
        from .frontend import ListenbrainzFrontend

        registry.add("frontend", ListenbrainzFrontend)

        from .backend import ListenbrainzBackend

        registry.add("backend", ListenbrainzBackend)
