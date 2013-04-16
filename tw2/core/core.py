from __future__ import absolute_import

from .util import thread_local


class WidgetError(Exception):
    "Base class for all widget errors."
    pass

request_local = thread_local
