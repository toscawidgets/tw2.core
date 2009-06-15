import util

class WidgetError(Exception):
    "Base class for all widget errors."
    pass

request_local = util.thread_local
