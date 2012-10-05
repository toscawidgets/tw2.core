from base import *
from contextlib import contextmanager

try:
    from nose.tools import assert_is_instance
except ImportError:
    from nose.tools import assert_true

    # Python 2.6 does not have assert_is_instance function
    def assert_is_instance(obj, cls, msg=None):
        assert_true(isinstance(obj, cls), msg)



# Python 2.6 have diferent assertRaises signature
class _AssertRaisesContext(object):
    """A context manager used to implement assert_raises* methods."""
    def __init__(self, expected):
        self.expected = expected
        self.failureException = AssertionError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "%s not raised" % (exc_name,))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        self.exception = exc_value  # store for later retrieval

        return True


def assert_raises(excClass):
    return _AssertRaisesContext(excClass)
