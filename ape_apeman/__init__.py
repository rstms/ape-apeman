"""Top-level package for ape-apeman."""

from .factory import APE
from .version import __author__, __email__, __timestamp__, __version__

__all__ = [
    "APE",
    "__version__",
    "__timestamp__",
    "__author__",
    "__email__",
]
