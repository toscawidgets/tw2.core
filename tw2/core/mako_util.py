import unicodedata
from mako.runtime import Undefined
from copy import copy

from markupsafe import Markup
from cgi import escape
import six
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

    new_attrs = [six.u('%s="%s"') % (k, escape(six.text_type(k in bools and k or v), True))
                 for k, v in six.iteritems(args)
                 if (k not in bools and v is not None) or (k in bools and v)]
    return Markup(six.u(" ").join(new_attrs))


def compat(context, attr):
    """ Backwards compatible widget attribute access.

    In tw1, all template attributes looked like:
        ${some_attribute}

    Whereas in tw2 they look like:
        ${w.some_attribute}

    This is a *nuisance* if you want to reuse a template between tw1 and tw2
    widgets.  With this function you can write:
        <%namespace name="tw" module="tw2.core.mako_util"/>
        ${tw.compat(attr='some_attribute')}
    or
        ${tw._('some_attribute')}

    Nice, right? :)
    """

    if not 'w' in context.keys():
        # Must be tw1
        return context.get(attr)
    else:
        # Must be tw2
        return getattr(context.get('w'), attr)


_ = compat  # Just for shorthand
