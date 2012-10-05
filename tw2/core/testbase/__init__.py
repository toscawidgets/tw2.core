from base import *

try:
    from nose.tools import assert_is_instance
except ImportError:
    from nose.tools import assert_true

    def assert_is_instance(obj, cls, msg=None):
        assert_true(isinstance(obj, cls), msg)
