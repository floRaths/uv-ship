from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('uv_ship')
except PackageNotFoundError:
    __version__ = 'unknown'

from . import config as cfg  # noqa: F401
