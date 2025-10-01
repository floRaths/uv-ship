from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('uv_ship')
except PackageNotFoundError:
    __version__ = 'unknown'

from . import changelogger as cl  # noqa: F401
from . import commands as cmd  # noqa: F401
from . import config as cfg  # noqa: F401
from . import messages as msg  # noqa: F401
