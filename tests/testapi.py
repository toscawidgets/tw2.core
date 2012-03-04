import tw2.core as twc
from tw2.core.testbase import base
from tw2.core.template import reset_engine_name_cache

twc.core.request_local = base.request_local_tst


def setup():
    base._request_local = {}
    base._request_id = None
    reset_engine_name_cache()


def request(requestid, mw=None):
    base._request_id = requestid
    rl = twc.core.request_local()
    rl.clear()
    rl['middleware'] = mw
    return base.request_local_tst()
