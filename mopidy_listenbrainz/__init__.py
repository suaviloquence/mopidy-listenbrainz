import pathlib
from importlib.metadata import distribution

import email.parser
from mopidy import config, ext

__dist_name__ = "Mopidy-Listenbrainz"


_dist = distribution(__dist_name__)
_pkg_info = _dist.read_text("METADATA") if _dist is not None else None
_metadata = email.parser.Parser().parsestr(_pkg_info)  # type: ignore

__version__ = _dist.version  # type: ignore
__author_contact__ = _metadata.get("Author-email")


class Extension(ext.Extension):

    dist_name = __dist_name__
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
        schema["search_schemes_fallback"] = config.List(optional=True)
        return schema

    def setup(self, registry):
        from .frontend import ListenbrainzFrontend

        registry.add("frontend", ListenbrainzFrontend)

        from .backend import ListenbrainzBackend

        registry.add("backend", ListenbrainzBackend)
