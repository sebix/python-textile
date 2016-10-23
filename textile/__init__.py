from __future__ import unicode_literals

import sys
import warnings

from .core import textile, textile_restricted, Textile
from .version import VERSION

__all__ = ['textile', 'textile_restricted']

__version__ = VERSION


if sys.version_info[:2] == (2, 6):
    warnings.warn(
        "Python 2.6 is no longer supported by the Python core team, please "
        "upgrade your Python. A future version of textile will drop support "
        "for Python 2.6",
        DeprecationWarning
    )
