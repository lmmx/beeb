from . import store

from . import __path__ as _dir_nspath
from pathlib import Path as _Path

__all__ = ["_dir_path"]

_dir_path = _Path(list(_dir_nspath)[0])