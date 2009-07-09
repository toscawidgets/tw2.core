import tw2.core as twc
from tw2.core.template import reset_engine_name_cache

def request_local_tst():
#    if _request_id is None:
#        raise KeyError('must be in a request')
    try:
        return _request_local[_request_id]
    except KeyError:
        rl_data = {}
        _request_local[_request_id] = rl_data
        return rl_data

twc.core.request_local = request_local_tst
_request_local = {}

def setup():
    global _request_local, _request_id
    _request_local = {}
    _request_id = None
    reset_engine_name_cache()


def request(requestid, mw=None):
    global _request_id
    _request_id = requestid
    rl = twc.core.request_local()
    rl.clear()
    rl['middleware'] = mw
    return request_local_tst()
