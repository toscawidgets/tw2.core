
import gettext
import os

import six

try:
    from pkg_resources import resource_filename
except ImportError:
    resource_filename = None

from speaklater import make_lazy_string

from . import core

import logging
log = logging.getLogger(__name__)


def get_localedir():
    """Get the location of locales."""
    locale_dir = ''
    if resource_filename is not None:
        try:
            locale_dir = resource_filename(__name__, "i18n")
        except NotImplementedError:
            pass
    if not hasattr(os, 'access'):
        return os.path.join(os.path.dirname(__file__), 'i18n')
    if os.access(locale_dir, os.R_OK | os.X_OK):
        return locale_dir
    locale_dir = os.path.join(os.path.dirname(__file__), 'i18n')
    if not os.access(locale_dir, os.R_OK | os.X_OK):
        locale_dir = os.path.normpath('/usr/share/locale')
    return locale_dir


def get_translator(lang=None, domain='tw2core', localedir=get_localedir()):
    if six.PY3:
        return gettext.translation(domain=domain, languages=lang,
                localedir=localedir, fallback=True).gettext
    else:
        return gettext.translation(domain=domain, languages=lang,
                localedir=localedir, fallback=True).ugettext


def tw2_translation_string(sval):

    def lookup_provided_translator(_sval):
        mw = core.request_local().get('middleware')
        if not mw:
            return _sval

        try:
            translator = get_translator(mw.config.get_lang())
        except AttributeError:
            try:
                translator = mw.config.translator
            except AttributeError:
                return _sval

        return translator(_sval)

    return make_lazy_string(lambda: lookup_provided_translator(sval))


_ = tw2_translation_string

__all__ = [
    'tw2_translation_string',
    '_',
]
