"""Utility functions, used internally.
"""
import copy, re, itertools, thread
import webob

_thread_local = {}
def thread_local():
    threadid = thread.get_ident()
    try:
        return _thread_local[threadid]
    except KeyError:
        rl_data = {}
        _thread_local[threadid] = rl_data
        return rl_data

import functools

class class_or_instance(object):
    def __init__(self, fn):
        self._function = fn
        self._wrapper = functools.wraps(fn)

    def __get__(self, ins, cls):
        return self._wrapper(functools.partial(self._function, ins, cls))

def name2label(name):
    """
    Convert a column name to a Human Readable name.
       1) Strip _id from the end
       2) Convert _ to spaces
       3) Convert CamelCase to Camel Case
       4) Upcase first character of Each Word
    """
    if name.endswith('_id'):
        name = name[:-3]
    return ' '.join([s.capitalize() for s in
               re.findall(r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)', name)])


class MultipleReplacer(object):
    """Performs several regexp substitutions on a string with a single pass.

    ``dct`` is a dictionary keyed by a regular expression string and with a
    callable as value that will get called to produce a subsituted value.

    The callable takes the matched text as first argument and may take any
    number of positional and keyword arguments. These arguments are any extra
    args passed when calling the instance.

    For performance, a single regular expression is built.

    Example::

        >>> string = "aaaabbbcc"
        >>> replacer = MultipleReplacer({
        ...     'a+':lambda g, context: g + context['after_a'],
        ...     'b+':lambda g, context: g + context['after_b'],
        ...     'c+':lambda g, context: context['before_c'] + g,
        ... })
        >>> replacer("aaaabbbcc", dict(
        ...     after_a = "1",
        ...     after_b = "2",
        ...     before_c = "3"
        ...     ))
        'aaaa1bbb23cc'
    """
    def __init__(self, dct, options=0):
        self._raw_regexp = r"|".join("(%s)" % k for k in dct.keys())
        self._substitutors = dct.values()
        self._regexp = re.compile(self._raw_regexp, options)

    def __repr__(self):
        return "<%s at %d (%r)>" % (self.__class__.__name__, id(self),
                                    self._raw_regexp)

    def _subsitutor(self, *args, **kw):
        def substitutor(match):
            for substitutor, group in itertools.izip(self._substitutors, match.groups()):
                if group is not None:
                    return substitutor(group, *args, **kw)
        return substitutor

    def __call__(self, string, *args, **kw):
        return self._regexp.sub(self._subsitutor(*args, **kw), string)

def abort(req, status):
    return webob.Response(request=req, status=status, content_type="text/html")

