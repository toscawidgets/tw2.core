import os, re, copy, tw2.core.middleware as tmw, tw2.core.template as template
import formencode as fe, itertools as it, pkg_resources as pk
from difflib import unified_diff
from cStringIO import StringIO
from BeautifulSoup import BeautifulSoup as bs
from nose.tools import eq_

#try:
import xml.etree.ElementTree as etree
from xml.parsers.expat import ExpatError
#except ImportError:
#    import cElementTree as etree

rendering_extension_lookup = {'mako':'mak', 'genshi':'html', 'cheetah':'tmpl', 'kid':'kid'}
rm = pk.ResourceManager()

def remove_whitespace_nodes(node):
    new_node = copy.copy(node)
    new_node._children = []
    if new_node.text and new_node.text.strip() == '':
        new_node.text = ''
    if new_node.tail and new_node.tail.strip() == '':
        new_node.tail = ''
    for child in node.getchildren():
        if child is not None:
            child = remove_whitespace_nodes(child)
        new_node.append(child)
    return new_node

def remove_namespace(doc):
    """Remove namespace in the passed document in place."""
    for elem in doc.getiterator():
        match = re.match('(\{.*\})(.*)', elem.tag)
        if match:
            elem.tag = match.group(2)

def replace_escape_chars(needle):
    needle = needle.replace('&nbsp;', ' ')
    needle = needle.replace(u'\xa0', ' ')
    return needle

_BOOLEAN_ATTRS = frozenset(['selected', 'checked', 'compact', 'declare',
                            'defer', 'disabled', 'ismap', 'multiple',
                            'nohref', 'noresize', 'noshade', 'nowrap'])

def replace_boolean_attrs(needle):
    """
    makes boolean attributes xml safe.
    """
    for attr in _BOOLEAN_ATTRS:
        eyelet = ' %s '%attr
        if eyelet in needle:
            needle = needle.replace(eyelet, '%s="%s" '%(attr, attr))
    return needle

def fix_xml(needle):
    needle = replace_escape_chars(needle)
    #first, we need to make sure the needle is valid html
    """
    try:
        validate_html(needle)
    except HTMLParser.HTMLParseError:
        print "error with: %s"%needle
        raise
    """
    #then we close all the open-ended tags to make sure it will compare properly
    needle = bs(needle).prettify()
    try:
        needle_node = etree.fromstring(needle)
    except ExpatError:
        raise ExpatError('Could not parse %s into xml.'%needle)
    needle_node = remove_whitespace_nodes(needle_node)
    remove_namespace(needle_node)
    needle_s = etree.tostring(needle_node)
    return needle_s

def in_xml(needle, haystack):
    try:
        needle_s = fix_xml(needle)
    except ExpatError:
        raise ExpatError('Could not parse needle: %s into xml.'%needle)
    try:
        haystack_s = fix_xml(haystack)
    except ExpatError:
        raise ExpatError('Could not parse haystack: %s into xml.'%haystack)
    return needle_s in haystack_s

def eq_xml(needle, haystack):
    needle_s, haystack_s = map(fix_xml, (needle, haystack))
    return needle_s == haystack_s

def assert_in_xml(needle, haystack):
    assert in_xml(needle, haystack), "%s not found in %s"%(needle, haystack)

def assert_eq_xml(needle, haystack):
    assert eq_xml(needle, haystack), "%s does not equal %s"%(needle, haystack)


import tw2.core as twc

def request_local_tst():
#    if _request_id is None:
#        raise KeyError('must be in a request')
    try:
        return _request_local[_request_id]
    except KeyError:
        rl_data = {}
        _request_local[_request_id] = rl_data
        return rl_data

import tw2.core.core
tw2.core.core.request_local = request_local_tst
from tw2.core.core import request_local

_request_local=None
_request_id=None


def TW2WidgetBuilder(widget, **attrs):
    class MyTestWidget(widget): pass
    for key, value in attrs.iteritems():
        setattr(MyTestWidget, key, value)
    return MyTestWidget

class WidgetTest(object):

    template_engine = 'string'
    params_as_vars = True
    widget = None
    attrs = {}
    params = {}
    expected = ""
    declarative = False
    validate_params = None

    def request(self, requestid, mw=None):
        if mw is None:
            mw = self.mw
        global _request_id
        _request_id = requestid
        rl = request_local()
        rl.clear()
        rl['middleware'] = mw
        return request_local_tst()

    def setup(self):
        global _request_id, _request_local
        _request_local = {}
        _request_id = None
        self.mw = tmw.make_middleware(None, default_engine=self.template_engine)
        if self.declarative:
            self.widget = TW2WidgetBuilder(self.widget, **self.attrs)
        return self.request(1)

    def _get_all_possible_engines(self):
        if self.widget is None:
            return
        template = self.widget.template
        try:
            engine, template_name = template.split(':', 1)
            yield engine
        except:
            for engine, ext in rendering_extension_lookup.iteritems():
                split = template.rsplit('.', 1)
                if(os.path.isfile(rm.resource_filename(split[0], '.'.join((split[1], ext))))):
                    yield engine

    def _check_rendering_vs_expected(self, engine, attrs, params, expected):
        _request_id = None
        template.reset_engine_name_cache()
        mw = tmw.make_middleware(None, preferred_rendering_engines=[engine])
        self.request(1, mw)
        r = self.widget(_no_autoid=True, **attrs).display(**params)
        # reset the cache as not to affect other tests
        assert_eq_xml(expected, r)


    def test_display(self):
        for engine in self._get_all_possible_engines():
            yield self._check_rendering_vs_expected, engine, self.attrs, self.params, self.expected

    def _check_validation(self, attrs, params, expected, raises=None):
        if raises is not None:
            try:
                r = self.widget(**attrs).validate(params)
            except raises, e:
                pass
            return
        r = self.widget(**attrs).validate(params)
        assert r == expected, r

    def test_validate(self):
        if self.validate_params is not None:
            for params in self.validate_params:
                if params[0] is None:
                    params[0] = self.attrs
                if len(params)<4:
                    params.append(None)
                yield self._check_validation, params[0], params[1], params[2], params[3]

class ValidatorTest(object):
    validator = None
    attrs = None
    params = None
    expected = None
    from_python_params = None
    from_python_attrs = None
    from_python_expected = None
    to_python_params = None
    to_python_attrs = None
    to_python_expected = None

    def __init__(self, *args, **kw):
        super(ValidatorTest, self).__init__(*args, **kw)
        for attr in ['attrs', 'params', 'expected',
                     'from_python_attrs', 'from_python_params', 'from_python_expected',
                     'to_python_attrs', 'to_python_params', 'to_python_expected']:
            value = getattr(self, attr)
            if value is not None and not isinstance(value, list):
                setattr(self, attr, [value,])

    def request(self, requestid, mw=None):
        if mw is None:
            mw = self.mw
        global _request_id
        _request_id = requestid
        rl = request_local()
        rl.clear()
        rl['middleware'] = mw
        return request_local_tst()

    def setup(self):
        global _request_id, _request_local
        _request_local = {}
        _request_id = None
        self.mw = tmw.make_middleware(None)
        return self.request(1)

    def _check_validation(self, attrs, params, expected, method='validate_python'):
        if isinstance(expected, type) and issubclass(expected, (twc.ValidationError, fe.Invalid)):
            try:
                r = getattr(self.validator(**attrs), method)(params)
            except expected:
                #XXX:figure out a way to test that the validation message matches
                pass
            return
        r = getattr(self.validator(**attrs), method)(params)
        eq_(r, expected)

    def test_validate(self):
        if self.expected:
            for attrs, params, expected in it.izip(self.attrs, self.params, self.expected):
                yield self._check_validation, attrs, params, expected

    def test_from_python(self):
        if self.from_python_expected:
            for attrs, params, expected in it.izip(self.from_python_attrs, self.from_python_params, self.from_python_expected):
                yield self._check_validation, attrs, params, expected, 'from_python'

    def test_to_python(self):
        if self.to_python_expected:
            for attrs, params, expected in it.izip(self.to_python_attrs, self.to_python_params, self.to_python_expected):
                yield self._check_validation, attrs, params, expected, 'to_python'
