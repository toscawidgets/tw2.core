import os
import re
import copy

import pkg_resources as pk

from difflib import unified_diff
from six import StringIO
from nose.tools import eq_
from nose import SkipTest

from .xhtmlify import (
    xhtmlify,
    ValidationError,
)

from sieve.operators import (
    eq_xml,
    in_xml,
    assert_eq_xml,
    assert_in_xml,
)

in_xhtml = in_xml
eq_xhtml = eq_xml
assert_in_xhtml = assert_in_xml
assert_eq_xhtml = assert_eq_xml

import xml.etree.ElementTree as etree
from xml.parsers.expat import ExpatError

import tw2.core as twc
import tw2.core.middleware as tmw
import tw2.core.templating as templating
import six

try:
    import formencode as fe
    possible_errors = (twc.ValidationError, fe.Invalid)
except ImportError:
    possible_errors = (twc.ValidationError,)

rm = pk.ResourceManager()

_BOOLEAN_ATTRS = frozenset(['selected', 'checked', 'compact', 'declare',
                            'defer', 'disabled', 'ismap', 'multiple',
                            'nohref', 'noresize', 'noshade', 'nowrap'])


def replace_boolean_attrs(needle):
    """
    makes boolean attributes xml safe.
    """
    for attr in _BOOLEAN_ATTRS:
        eyelet = ' %s ' % attr
        if eyelet in needle:
            needle = needle.replace(eyelet, '%s="%s" ' % (attr, attr))
    return needle


def request_local_tst():
#    if _request_id is None:
#        raise KeyError('must be in a request')

    global _request_local
    if _request_local is None:
        _request_local = {}

    try:
        return _request_local[_request_id]
    except KeyError:
        rl_data = {}
        _request_local[_request_id] = rl_data
        return rl_data

import tw2.core.core
tw2.core.core.request_local = request_local_tst
from tw2.core.core import request_local

_request_local = None
_request_id = None


def TW2WidgetBuilder(widget, **attrs):
    class MyTestWidget(widget):
        pass

    for key, value in six.iteritems(attrs):
        setattr(MyTestWidget, key, value)
    return MyTestWidget


class Base(object):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def skipTest(self, msg):
        raise SkipTest(msg)


class WidgetTest(Base):
    """
    This class provides a basis for testing all widget classes.  It's setup
    will automatically create a request, and a widget of the type specified.
    It will also test the display function by comparing it against an
    expected output.

    `template_engine`
        Default template engine for the displays_on property of the TestCase's
        middleware

    `params_as_vars`
        Also passed into the middleware

    `widget`
        Class of the widget to test

    `attrs`
        attributes to pass into the widget at creation

    `params`
        params to send into the widget on the "display" call

    `expected`
        xhtml stream representing the expected output

    `declarative`
        whether or not the widget shoudl be created in a declarative manner.

    `validate_params`
        A list of conditions to test against the widget.  The list contains a
        set of sub-lists, which have the following format:

        [0] - Params to send into the widget's init

        [1] - Params sent into the widget's validate method

        [2] - expected output

        [3] - the expected validation error type (optional)

    `wrap`
        Wrap expected and the result in an element.  Useful if the template
        generates an xml snippet with more than one top level element.

    `engines`
        A list of engines to try tests with.  Defaults to all of them.

    """

    template_engine = 'string'
    params_as_vars = True
    widget = None
    attrs = {}
    params = {}
    expected = ""
    declarative = False
    validate_params = None
    wrap = False
    engines = templating._default_rendering_extension_lookup.keys()


    def setUp(self):
        global _request_id, _request_local
        _request_local = {}
        _request_id = None

        super(WidgetTest, self).setUp()

        self.mw = tmw.make_middleware(
            None,
            default_engine=self.template_engine
        )
        if self.declarative:
            self.widget = TW2WidgetBuilder(self.widget, **self.attrs)

        return self.request(1)


    def request(self, requestid, mw=None):
        if mw is None:
            mw = self.mw
        global _request_id
        _request_id = requestid
        rl = request_local()
        rl.clear()
        rl['middleware'] = mw
        return request_local_tst()

    def _get_all_possible_engines(self):
        for engine in templating._default_rendering_extension_lookup:
            yield engine

    def _check_rendering_vs_expected(self, engine, attrs, params, expected):
        if self.engines and engine not in self.engines:
            raise SkipTest("%r not in engines %r" % (engine, self.engines))
        _request_id = None
        templating.engine_name_cache = {}
        mw = tmw.make_middleware(None, preferred_rendering_engines=[engine])
        self.request(1, mw)
        try:
            r = self.widget(_no_autoid=True, **attrs).display(**params)
        except ValueError as e:
            if str(e).startswith("Could not find engine name"):
                raise SkipTest("No template for engine %r" % engine)
            else:
                raise

        # reset the cache as not to affect other tests
        assert_eq_xml(r, expected, self.wrap)

    def test_display(self):
        if not self.widget:
            return

        for engine in self._get_all_possible_engines():
            yield self._check_rendering_vs_expected, \
                    engine, self.attrs, self.params, self.expected

    def _check_validation(self, attrs, params, expected, raises=None):
        if raises is not None:
            try:
                r = self.widget(**attrs).validate(params)
            except raises as e:
                pass
            return
        r = self.widget(**attrs).validate(params)
        eq_(expected, r)

    def test_validate(self):
        if self.validate_params is not None:
            for params in self.validate_params:
                if params[0] is None:
                    params[0] = self.attrs
                if len(params) < 4:
                    params.append(None)
                yield self._check_validation, \
                    params[0], params[1], params[2], params[3]


class ValidatorTest(Base):
    """
    This test provides a basis for testing all validator classes. On
    initialization, this class will make a request and a middleware
    instance for use in testing.

    It will then test the validator's validate, to_python, and from_python
    methods.

    `validator`
        class to create the validator from

    `attrs`
        attributes sent into the validator on instantiation

    `params`
        list of parameters sent into test the validator's validate method

    `expected`
        list of expected outputs for the validator's validate method

    `from_python_attrs`
        attributes sent into the validator on instantiation for from python
        tests

    `from_python_params`
        list of parameters sent into test the validator's from_python method

    `from_python_expected`
        list of expected outputs for the validator's from_python method

    `to_python_attrs`
        attributes sent into the validator on instantiation for from python
        tests

    `to_python_params`
        list of parameters sent into test the validator's to_python method

    `to_python_expected`
        list of expected outputs for the validator's to_python method
    """
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
        attrs = [
            'attrs',
            'params',
            'expected',
            'from_python_attrs',
            'from_python_params',
            'from_python_expected',
            'to_python_attrs',
            'to_python_params',
            'to_python_expected'
        ]
        for attr in attrs:
            value = getattr(self, attr)
            if value is not None and not isinstance(value, list):
                setattr(self, attr, [value, ])

    def request(self, requestid, mw=None):
        if mw is None:
            mw = self.mw
        global _request_id
        _request_id = requestid
        rl = request_local()
        rl.clear()
        rl['middleware'] = mw
        return request_local_tst()

    def _check_validation(self, attrs, params, expected,
                          method='to_python'):
        vld = self.validator(**attrs)
        if isinstance(expected, type) and \
            issubclass(expected, possible_errors):
            try:
                if method == 'to_python':
                    params = vld.to_python(params)
                r = getattr(vld, method)(params)
            except expected:
                # XXX: figure out test way to test validation message match
                pass
            return
        if method == 'to_python':
            params = vld.to_python(params)
        r = getattr(vld, method)(params)
        eq_(r, expected)

    def test_validate(self):
        if self.expected:
            triples = six.moves.zip(self.attrs, self.params, self.expected)
            for attrs, params, expected in triples:
                yield self._check_validation, \
                    attrs, params, expected

    def test_from_python(self):
        if self.from_python_expected:
            triples = six.moves.zip(
                self.from_python_attrs,
                self.from_python_params,
                self.from_python_expected,
            )
            for attrs, params, expected in triples:
                yield self._check_validation, \
                    attrs, params, expected, 'from_python'

    def test_to_python(self):
        name = self.__class__.__name__
        tbv =  name == 'TestBoolValidator'
        if self.to_python_expected:
            triples = six.moves.zip(
                self.to_python_attrs,
                self.to_python_params,
                self.to_python_expected,
            )
            for attrs, params, expected in triples:
                yield self._check_validation, \
                    attrs, params, expected, 'to_python'

import webob as wo
import webtest as wt
import tw2.core as twc
import os


class TestInPage(Base):
    content_type = 'text/html'
    charset = 'UTF8'

    html = "<html><head><title>TITLE</title></head><body>%s</body></html>"

    def __call__(self, environ, start_response):
        req = wo.Request(environ)
        resp = wo.Response(
            request=req,
            content_type="%s; charset=%s" % (
                self.content_type, self.charset
            )
        )
        if hasattr(self, 'custom_display'):
            widg = self.custom_display()
        else:
            widg = self.inject_widget.display()
        resp.unicode_body = self.html % widg
        return resp(environ, start_response)



class TestInPageTest(TestInPage):
    def test_base(self):
        res = self.app.get('/')
        assert_in_xhtml(
            '<script type="text/javascript" src="paj" ></script>',
            res.body
        )
        assert_in_xhtml(
            '<link type="text/css" rel="stylesheet" media="all" href="joe" />',
            res.body
        )
        assert_in_xhtml(
            '<p>TEST test</p>',
            res.body
        )
