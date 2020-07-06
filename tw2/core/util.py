""" Utility functions, used internally. """

import copy
import re
import functools
import six.moves

try:
    # py2
    import thread
except ImportError:
    # py3
    import _thread as thread

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
    callable as value that will get called to produce a substituted value.

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

    def _substitutor(self, *args, **kw):
        def substitutor(match):
            tuples = six.moves.zip(self._substitutors, match.groups())
            for substitutor, group in tuples:
                if group is not None:
                    return substitutor(group, *args, **kw)
        return substitutor

    def __call__(self, string, *args, **kw):
        return self._regexp.sub(self._substitutor(*args, **kw), string)


def abort(req, status):
    return webob.Response(request=req, status=status, content_type="text/html")


_memoization_flush_callbacks = []


class memoize(object):
    def __init__(self, f):
        global _memoization_flush_callbacks
        self.f = f
        self.mem = {}
        _memoization_flush_callbacks.append(self._flush)

    def _flush(self):
        self.mem = {}

    def __call__(self, *args, **kwargs):
        if (args, str(kwargs)) in self.mem:
            return self.mem[args, str(kwargs)]
        else:
            tmp = self.f(*args, **kwargs)
            self.mem[args, str(kwargs)] = tmp
            return tmp


def flush_memoization():
    for cb in _memoization_flush_callbacks:
        cb()


def clone_object(obj, **values):
    if obj is None:
        obj = type('_TemporaryObject', (object,), {})()
    else:
        obj = copy.copy(obj)

    # NOTE: upstream doesn't consider obj being a dict
    if isinstance(obj, dict):
        return obj

    for k,v in values.items():
        setattr(obj, k, v)

    return obj


# relpath support for python-2.5
# Taken from https://github.com/nipy/nipype/issues/62
# Related to https://github.com/toscawidgets/tw2.core/issues/30
try:
    from os.path import relpath
except ImportError:
    import os
    import os.path as op

    def relpath(path, start=None):
        """Return a relative version of a path"""
        if start is None:
            start = os.curdir
        if not path:
            raise ValueError("no path specified")
        start_list = op.abspath(start).split(op.sep)
        path_list = op.abspath(path).split(op.sep)

        if start_list[0].lower() != path_list[0].lower():
            unc_path, rest = op.splitunc(path)
            unc_start, rest = op.splitunc(start)
            if bool(unc_path) ^ bool(unc_start):
                raise ValueError(
                    "Cannot mix UNC and non-UNC paths (%s and%s)" %
                    (path, start))
            else:
                raise ValueError(
                    "path is on drive %s, start on drive %s"
                    % (path_list[0], start_list[0]))

        # Work out how much of the filepath is shared by start and path.
        for i in range(min(len(start_list), len(path_list))):
            if start_list[i].lower() != path_list[i].lower():
                break
        else:
            i += 1

        rel_list = [op.pardir] * (len(start_list) - i) + path_list[i:]
        if not rel_list:
            return os.curdir
        return op.join(*rel_list)
