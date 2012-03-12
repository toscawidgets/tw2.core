from speaklater import make_lazy_string

import core

import traceback
import logging
log = logging.getLogger(__name__)

def tw2_translation_string(sval):
    def lookup_provided_translator(_sval):
        mw = core.request_local().get('middleware')
        if not mw:
            return _sval

        try:
            return core.request_local()['middleware'].config.translator(_sval)
        except TypeError as e:
            log.warn(traceback.format_exc())
            return _sval

    return make_lazy_string(lambda: lookup_provided_translator(sval))

_ = tw2_translation_string

__all__ = [
    'tw2_translation_string',
    '_',
]
