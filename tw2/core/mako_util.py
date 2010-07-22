import unicodedata
from mako.runtime import Undefined
from copy import copy

from cgi import escape
#from mako.filters import xml_escape

__all__ = ["attrs"]

_BOOLEAN_ATTRS = frozenset(['selected', 'checked', 'compact', 'declare',
                            'defer', 'disabled', 'ismap', 'multiple',
                            'nohref', 'noresize', 'noshade', 'nowrap'])

def attrs(context, args=None, attrs=None):
    # Emulates Genshi's AttrsDirective (poorly)
    if isinstance(args, list):
        args = dict(args)
    if not args:
        args = {}
    else:
        args = copy(args)
    if attrs:
        args.update(attrs)
    bools = _BOOLEAN_ATTRS

    new_attrs = [u'%s="%s"' % (k, escape(unicode(k in bools and k or v), True))
                      for k,v in args.iteritems() if (k not in bools and v is not None) or (k in bools and v)]
    return u" ".join(new_attrs)
