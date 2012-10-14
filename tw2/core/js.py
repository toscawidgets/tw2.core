"""
Python-JS interface to dynamically create JS function calls from your widgets.

This moudle doesn't aim to serve as a Python-JS "translator". You should code
your client-side code in JavaScript and make it available in static files which
you include as JSLinks or inline using JSSources. This module is only intended
as a "bridge" or interface between Python and JavaScript so JS function
**calls** can be generated programatically.
"""
import re
import sys

import logging
from itertools import imap
import simplejson.encoder

__all__ = ["js_callback", "js_function", "js_symbol", "encode"]

log = logging.getLogger(__name__)


class TWEncoder(simplejson.encoder.JSONEncoder):
    """A JSON encoder that can encode Widgets, js_calls, js_symbols and
    js_callbacks.

    Example::

        >>> encode = TWEncoder().encode
        >>> print encode({
        ...     'onLoad': js_function("do_something")(js_symbol("this"))
        ... })
        {"onLoad": do_something(this)}

        >>> from tw2.core.api import Widget
        >>> w = Widget("foo")
        >>> args = {
        ...    'onLoad': js_callback(
        ...         js_function('jQuery')(w).click(js_symbol('onClick'))
        ...     )
        ... }
        >>> print encode(args)
        {"onLoad": function(){jQuery(\\"foo\\").click(onClick)}}
        >>> print encode({'args':args})
        {"args": {"onLoad": function(){jQuery(\\"foo\\").click(onClick)}}}
    """

    def __init__(self, *args, **kw):
        # This makes encoded objects be prettily formatted.  It is very nice
        # for debugging and should be made configurable at some point.
        # TODO -- make json encoding pretty-printing configurable
        #kw['indent'] = '  '

        self.unescape_pattern = re.compile('"TW2Encoder_unescape_([0-9]*)"')
        self.pass_through = (_js_call, js_callback, js_symbol, js_function)
        super(TWEncoder, self).__init__(*args, **kw)

        # This is required to get encoding of _js_call to work
        self.namedtuple_as_object = False

    def default(self, obj):
        if isinstance(obj, self.pass_through):
            result = self.mark_for_escape(obj)
            return result

        if hasattr(obj, '__json__'):
            return obj.__json__()

        if hasattr(obj, 'id'):
            return str(obj.id)

        return super(TWEncoder, self).default(obj)

    def encode(self, obj):
        self.unescape_symbols = {}
        encoded = super(TWEncoder, self).encode(obj)
        unescaped = self.unescape_marked(encoded)
        self.unescape_symbols = {}
        return unescaped

        encoded = super(TWEncoder, self).encode(obj)
        return self.unescape_marked(encoded)

    def mark_for_escape(self, obj):
        self.unescape_symbols[id(obj)] = obj
        return 'TW2Encoder_unescape_' + str(id(obj))

    def unescape_marked(self, encoded):
        def unescape(match):
            obj_id = int(match.group(1))
            obj = self.unescape_symbols[obj_id]
            return str(obj)

        return self.unescape_pattern.sub(unescape, encoded)


encoder = None  # This gets reset at the bottom of the file.


class js_symbol(object):
    def __init__(self, name=None, src=None):
        if name == None and src == None:
            raise ValueError("js_symbol must be given name or src")
        if name and src:
            raise ValueError("js_symbol must not be given name and src")
        if src != None:
            self._name = src
        else:
            self._name = name

    def __str__(self):
        return str(self._name)


class js_callback(object):
    """A js function that can be passed as a callback to be called
    by another JS function

    Examples:

    >>> str(js_callback("update_div"))
    'update_div'

    >>> str(js_callback("function (event) { .... }"))
    'function (event) { .... }'

    Can also create callbacks for deferred js calls

    >>> str(js_callback(js_function('foo')(1,2,3)))
    'function(){foo(1, 2, 3)}'

    Or equivalently

    >>> str(js_callback(js_function('foo'), 1,2,3))
    'function(){foo(1, 2, 3)}'

    A more realistic example

    >>> jQuery = js_function('jQuery')
    >>> my_cb = js_callback('function() { alert(this.text)}')
    >>> on_doc_load = jQuery('#foo').bind('click', my_cb)
    >>> call = jQuery(js_callback(on_doc_load))
    >>> print call
    jQuery(function(){jQuery(\\"#foo\\").bind(
        \\"click\\", function() { alert(this.text)})})

    """
    def __init__(self, cb, *args):
        if isinstance(cb, basestring):
            self.cb = cb
        elif isinstance(cb, js_function):
            self.cb = "function(){%s}" % cb(*args)
        elif isinstance(cb, _js_call):
            self.cb = "function(){%s}" % cb
        else:
            self.cb = ''

    def __call__(self, *args):
        raise TypeError("A js_callback cannot be called from Python")

    def __str__(self):
        return self.cb


class js_function(object):
    """A JS function that can be "called" from python and and added to
    a widget by widget.add_call() so it get's called every time the widget
    is rendered.

    Used to create a callable object that can be called from your widgets to
    trigger actions in the browser. It's used primarily to initialize JS code
    programatically. Calls can be chained and parameters are automatically
    json-encoded into something JavaScript undersrtands. Example::

    >>> jQuery = js_function('jQuery')
    >>> call = jQuery('#foo').datePicker({'option1': 'value1'})
    >>> str(call)
    'jQuery("#foo").datePicker({"option1": "value1"})'

    Calls are added to the widget call stack with the ``add_call`` method.

    If made at Widget initialization those calls will be placed in
    the template for every request that renders the widget.

    >>> import tw2.core as twc
    >>> class SomeWidget(twc.Widget):
    ...     pickerOptions = twc.Param(default={})
    >>> SomeWidget.add_call(
    ...     jQuery('#%s' % SomeWidget.id).datePicker(SomeWidget.pickerOptions)
    ... )

    More likely, we will want to dynamically make calls on every
    request.  Here we will call add_calls inside the ``prepare`` method.

    >>> class SomeWidget(Widget):
    ...     pickerOptions = twc.Param(default={})
    ...     def prepare(self):
    ...         super(SomeWidget, self).prepare()
    ...         self.add_call(
    ...             jQuery('#%s' % d.id).datePicker(d.pickerOptions)
    ...         )

    This would allow to pass different options to the datePicker on every
    display.

    JS calls are rendered by the same mechanisms that render required css and
    js for a widget and places those calls at bodybottom so DOM elements which
    we might target are available.

    Examples:

    >>> call = js_function('jQuery')("a .async")
    >>> str(call)
    'jQuery("a .async")'

    js_function calls can be chained:

    >>> call = js_function('jQuery')("a .async").foo().bar()
    >>> str(call)
    'jQuery("a .async").foo().bar()'

    """

    def __init__(self, name):
        self.__name = name

    def __call__(self, *args):
        return _js_call(self.__name, [], args, called=True)

    def __str__(self):
        return self.__name


class _js_call(object):
    __slots__ = ('__name', '__call_list', '__args', '__called')

    def __init__(self, name, call_list, args=None, called=False):
        self.__name = name
        self.__args = args
        call_list.append(self)
        self.__call_list = call_list
        self.__called = called

    def __getattr__(self, name):
        return self.__class__(name, self.__call_list)

    def __call__(self, *args):
        self.__args = args
        self.__called = True
        return self

    def __get_js_repr(self):
        if self.__called:
            args = self.__args
            rep = '%s(%s)' % (
                self.__name,
                ', '.join(imap(encoder.encode, args))
            )
            return rep\
                    .replace('\\"', '"')\
                    .replace("\\'", "'")\
                    .replace('\\n', '\n')
        else:
            return self.__name

    def __str__(self):
        if not self.__called:
            raise TypeError('Last element in the chain has to be called')
        return '.'.join(c.__get_js_repr() for c in self.__call_list)

    def __unicode__(self):
        return str(self).decode(sys.getdefaultencoding())

encoder = TWEncoder()
