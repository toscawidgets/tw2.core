import webob as wo, webtest as wt, tw2.core as twc, os, testapi, tw2.core.resources as twr, tw2.core.testbase as tb, tw2.core.params as pm
import tw2.core.core
from nose.tools import eq_, raises
from sieve.operators import eq_xml as eq_xhtml
import unittest
from six.moves import map
from six.moves import zip
import six

js = twc.JSLink(link='paj')
css = twc.CSSLink(link='joe')
csssrc = twc.CSSSource(src='.bob { font-weight: bold; }')
jssrc = twc.JSSource(src='bob')

TestWidget = twc.Widget(template='genshi:tw2.core.test_templates.inner_genshi', test='test')
html = "<html><head><title>a</title></head><body>hello</body></html>"

inject_widget = TestWidget(id='a', resources=[js])

def simple_app(environ, start_response):
    req = wo.Request(environ)
    ct = 'text/html' if req.path == '/' else 'test/plain'
    resp = wo.Response(request=req, content_type="%s; charset=UTF8" % ct)
    inject_widget.display()
    if six.PY3:
        resp.text = html
    else:
        resp.body = html
    return resp(environ, start_response)

mw = twc.make_middleware(simple_app)
tst_mw = wt.TestApp(mw)

class TestResources(object):
    def setUp(self):
        testapi.setup()

    def test_res_collection(self):
        rl = testapi.request(1, mw)
        wa = TestWidget(id='a')
        wb = TestWidget(id='b', resources=[js, css])
        wa.display()
        rl = twc.core.request_local()
        assert(len(rl.get('resources', [])) == 0)
        wb.display()
        for r in rl['resources']:
            assert(any(isinstance(r, b) for b in [js, css]))
        rl = testapi.request(2)
        r = rl.get('resources', [])
        assert len(r) == 0, r

    def test_res_nodupe(self):
        wa = TestWidget(id='a', resources=[js])
        wb = TestWidget(id='b', resources=[twc.JSLink(link='paj')])
        wc = TestWidget(id='c', resources=[twc.JSLink(link='test')])
        wd = TestWidget(id='d', resources=[css])
        we = TestWidget(id='e', resources=[twc.CSSLink(link='joe')])

        rl = testapi.request(1, mw)
        wa.display()
        wb.display()
        rl = twc.core.request_local()
        r = rl['resources']
        assert(len(rl['resources']) == 1)
        wc.display()
        assert(len(rl['resources']) == 2)
        wd.display()
        we.display()
        assert(len(rl['resources']) == 3)

    def test_res_order(self):
        """ Expect [foo1 foo3 foo2 foo4] since foo2 depends on foo3 """
        foo1 = twc.JSLink(link='foo1')
        foo3 = twc.JSLink(link='foo3')
        foo2 = twc.JSLink(link='foo2', resources=[foo3])
        foo4 = twc.JSLink(link='foo4')
        wa = TestWidget(id='a', resources=[foo1, foo2, foo4])

        rl = testapi.request(1, mw)
        wa.display()
        rl = twc.core.request_local()

        lnk = lambda r: r.link
        eq_(
            list(map(lnk, rl['resources'])),
            list(map(lnk, [foo1, foo3, foo2, foo4]))
        )


    #--
    # ResourcesApp
    #--
    def test_not_found(self):
        #assert(tst_mw.get('/fred', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/test', expect_errors=True).status == '404 Not Found')

    def test_serve(self):
        mw.resources.register('tw2.core', 'test_templates/simple_genshi.html')
        fcont = open(os.path.join(os.path.dirname(twc.__file__), 'test_templates/simple_genshi.html'), 'rb').read()
        assert(tst_mw.get('/resources/tw2.core/test_templates/simple_genshi.html').body == fcont)
        assert(tst_mw.get('/resources/tw2.core/test_templates/notexist', expect_errors=True).status == '404 Not Found')

    def test_different_file(self):
        mw.resources.register('tw2.core', 'test_templates/simple_genshi.html')
        assert(tst_mw.get('/resources/tw2.tests/simple_kid.kid', expect_errors=True).status == '404 Not Found')

    def test_whole_dir(self):
        mw.resources.register('tw2.core', 'test_templates/', whole_dir=True)
        fcont = open(os.path.join(os.path.dirname(twc.__file__), 'test_templates/simple_genshi.html'), 'rb').read()
        eq_(tst_mw.get('/resources/tw2.core/test_templates/simple_genshi.html').body, fcont)
        eq_(tst_mw.get('/resources/tw2.core/test_templates/notexist', expect_errors=True).status, '404 Not Found')

    def test_dir_traversal(self): # check for potential security flaw
        mw.resources.register('tw2.core', 'test_templates/')
        assert(tst_mw.get('/resources/tw2.tests/__init__.py', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/tw2.core/test_templates/../__init__.py', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/tw2.core/test_templates/..\\__init__.py', expect_errors=True).status == '404 Not Found')

    def test_whole_dir_traversal(self): # check for potential security flaw
        mw.resources.register('tw2.core', 'test_templates/', whole_dir=True)
        assert(tst_mw.get('/resources/tw2.tests/__init__.py', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/tw2.core/test_templates/../__init__.py', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/tw2.core/test_templates/..\\__init__.py', expect_errors=True).status == '404 Not Found')

    def test_zipped(self):
        # assumes webtest is installed as a zipped egg
        mw.resources.register('webtest', '__init__.py')
        assert(tst_mw.get('/resources/webtest/__init__.py').body.startswith(six.b('# (c) 2005 Ian')))

    def test_cache_header(self):
        mw.resources.register('tw2.core', 'test_templates/simple_genshi.html')
        cache = tst_mw.get('/resources/tw2.core/test_templates/simple_genshi.html').headers['Cache-Control']
        assert(cache == 'max-age=3600')

    #--
    # Links register resources
    #--
    def test_link_reg(self):
        testapi.request(1, mw)
        wa = twc.JSLink(modname='tw2.core', filename='test_templates/simple_mako.mak').req()
        wa.prepare()
        assert(wa.link == '/resources/tw2.core/test_templates/simple_mako.mak')
        tst_mw.get(wa.link)

    def test_mime_type(self):
        testapi.request(1, mw)
        wa = twc.JSLink(modname='tw2.core', filename='test_templates/simple_genshi.html').req()
        wa.prepare()
        resp = tst_mw.get(wa.link)
        assert(resp.content_type == 'text/html')
        assert(resp.charset == 'UTF-8')

    #--
    # Resource injector
    #--
    def test_no_inject_head(self):
        rl = testapi.request(1, mw)
        js.req(no_inject=True).prepare()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head><title>a</title></head><body>hello</body></html>')

    def test_inject_head(self):
        rl = testapi.request(1, mw)
        js.inject()
        csssrc.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head><script type="text/javascript" src="paj"></script>\
            <style type="text/css">.bob { font-weight: bold; }</style>\
            <title>a</title></head><body>hello</body></html>')

    def test_inject_body(self):
        rl = testapi.request(1, mw)
        jssrc.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head><title>a</title></head><body>hello<script type="text/javascript">bob</script></body></html>')

    def test_inject_css(self):
        rl = testapi.request(1, mw)
        csssrc.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head><style type="text/css">.bob { font-weight: bold; }</style>\
            <title>a</title></head><body>hello</body></html>')

    def test_inject_both(self):
        rl = testapi.request(1, mw)
        js.inject()
        jssrc.inject()
        csssrc.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head><script type="text/javascript" src="paj"></script>\
            <style type="text/css">.bob { font-weight: bold; }</style>\
            <title>a</title></head><body>hello<script type="text/javascript">bob</script>\
            </body></html>')

    def test_inject_js_twice(self):
        rl = testapi.request(1, mw)
        js.inject()
        js.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head>\
            <script type="text/javascript" src="paj"></script>\
            <title>a</title></head><body>hello</body></html>')

    def test_inject_jssrc_twice(self):
        rl = testapi.request(1, mw)
        jssrc.inject()
        jssrc.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head>\
            <title>a</title></head><body>hello<script type="text/javascript">bob</script>\
            </body></html>')

    def test_inject_csssrc_twice(self):
        rl = testapi.request(1, mw)
        csssrc.inject()
        csssrc.inject()
        out = twc.inject_resources(html)
        assert eq_xhtml(out, '<html><head>\
            <style type="text/css">.bob { font-weight: bold; }</style>\
            <title>a</title></head><body>hello</body></html>')

    def test_detect_clear(self):
        widget = twc.Widget(id='a', template='genshi:tw2.core.test_templates.inner_genshi', test='test', resources=[js])
        rl = testapi.request(1, mw)
        eq_(rl.get('resources', []), [])
        widget.display()
        rl = twc.core.request_local()
        assert(len(rl.get('resources', [])) == 1)
        out = twc.inject_resources(html)
        eq_(rl.get('resources', []), [])

    #--
    # General middleware
    #--
    def test_mw_resourcesapp(self):
        testapi.request(1)
        mw.resources.register('tw2.core', 'test_templates/simple_genshi.html')
        fcont = open(os.path.join(os.path.dirname(twc.__file__), 'test_templates/simple_genshi.html'), 'rb').read()
        assert(tst_mw.get('/resources/tw2.core/test_templates/simple_genshi.html').body == fcont)

    def test_mw_clear_rl(self):
        rl = testapi.request(1)
        rl['blah'] = 'lah'
        tst_mw.get('/')
        rl = twc.core.request_local()
        assert(rl == {})

    def test_mw_inject(self):
        testapi.request(1, mw)
        assert eq_xhtml(tst_mw.get('/').body, '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello</body></html>')

    def test_mw_inject_html_only(self):
        testapi.request(1, mw)
        eq_(tst_mw.get('/plain').body, six.b(html))

class __TestDirLink(tb.WidgetTest):
    """seems like dirlink is not implemented yet"""
    widget = twr.DirLink
    attrs = {'template':'something'}
    expected = '<script type="text/javascript" src="something"></script>'

class TestJSLink(tb.WidgetTest):
    widget = twr.JSLink
    attrs = {'link':'something'}
    expected = '<script type="text/javascript" src="something"></script>'

    @raises(pm.ParameterError)
    def test_no_filename(self):
        twr.JSLink().display()

class TestCssLink(tb.WidgetTest):
    widget = twr.CSSLink
    attrs = {'link':'something'}
    expected = '<link rel="stylesheet" type="text/css" href="something" media="all"/>'


class TestJsSource(tb.WidgetTest):
    widget = twr.JSSource
    attrs = {'src':'something'}
    expected = '<script type="text/javascript">something</script>'

    def _check_rendering_vs_expected(self, engine, *args, **kw):
        base = super(TestJsSource, self)
        return base._check_rendering_vs_expected(engine, *args, **kw)

    def _test_repr_(self):
        #not sure how to test resources.py:79
        r = repr(self.widget(**self.attrs))
        assert r == "<class 'tw2.core.params.JSSource_s'>", r


class TestJsFuncall(tb.WidgetTest):
    widget = twr._JSFuncCall
    attrs = {'function':'foo', 'args':['a', 'b']}
    expected = None

    def test_display(self):
        for engine in self._get_all_possible_engines():
            yield self._check_equal, engine

    def _check_equal(self, engine):
        r = self.widget(**self.attrs).display(
            template='%s:%s' % (engine, twr._JSFuncCall.template))
        eq_(r, '<script type="text/javascript">foo("a", "b")</script>')

class TestJSSourceEscaping(tb.WidgetTest):
    widget = twr.JSSource
    attrs = {}
    expected = None
    s = twr.JSSource(src='''
function test(a, b) {
    if (b < 5)
        return b;
    else
        return "OK";
}
''')

    compare_to = None

    def test_display(self):
        for engine in self._get_all_possible_engines():
            yield self._check_equal, engine

    def _check_equal(self, engine):
        r = self.s.req()
        display = r.display(
            template='%s:%s' % (engine, twr.JSSource.template)).strip()
        if self.compare_to is None:
            self.compare_to = display
        else:
            eq_(display, self.compare_to)

class TestCSSSourceEscaping(tb.WidgetTest):
    widget = twr.CSSSource
    attrs = {}
    expected = None
    s = twr.CSSSource(src='''
p > strong:after {
    content:"WOAH, this was STRONG!";
}
''')


    compare_to = None

    def test_display(self):
        for engine in self._get_all_possible_engines():
            yield self._check_equal, engine

    def _check_equal(self, engine):
        if engine in ['chameleon']:
            self.skipTest("CSSSource is missing a pt template.")

        r = self.s.req()
        display = r.display(
            template='%s:%s' % (engine, twr.CSSSource.template)).strip()
        if self.compare_to is None:
            self.compare_to = display
        else:
            eq_(display, self.compare_to)

from pkg_resources import Requirement
class TestResourcesApp:

    def setup(self):
        class Config(object):pass
        config = Config()
        config.res_prefix = ""
        config.script_name = ''
        self.app = twr.ResourcesApp(config)

    def test_register_requirement(self):
        req = Requirement.parse('tw2.core>1.0')
        self.app.register(req, 'something.txt')

def test_find_charset():
    eq_(twc.resources.find_charset('charset=iso-8859-1'), 'iso-8859-1')


class TestResourcesMisc(unittest.TestCase):

    def testJSSymbol(self):
        """
        should set the src attribute
        """
        s = twr.JSSymbol("source")
        self.assert_(s.src == "source")

    def testEncoderDefault(self):
        enc = twc.encoder
        enc.encode("")
        res = enc.default(twr.JSSymbol("X"))
        self.assert_(res.startswith("TW2Encoder_unescape_"))

        try:
            res = enc.default(None)
            self.assert_(False)
        except TypeError as te:
            self.assert_(str(te).endswith("is not JSON serializable"))

    def testUnEscapeMarked(self):
        enc = twc.encoder
        data = dict(foo=twr.JSSymbol("foo"),
                    bar=twr.JSSymbol("bar"))
        res = enc.unescape_marked(enc.encode(data))
        self.assert_("foo" in  res, res)
        self.assert_("bar" in res, res)

    def testEncoderEmbedded(self):
        """ JQGrid Issue #6

        https://github.com/toscawidgets/tw2.jqplugins.jqgrid/issues/6
        """
        enc = twc.encoder
        data = {
            'rowlist': [30, 60, 100],
        }
        result = enc.encode(data)

        class Widget(twc.Widget):
            inline_engine_name = "mako"
            template = "${w.options | n}"
            # If template is set to the following, then this fails.
            #template = "${w.options}"
            options = result

        eq_(Widget.display().strip(), result.strip())

    def testLinkHash(self):
        l = twr.Link(link="http://google.com")
        self.assert_(hash(l.req()))  # meh

    def testAutoModname(self):
        l = twr.Link(filename="somefile")
        eq_(l.modname, __name__)

    def testAutoModnameReqPrep(self):
        l = twr.Link(filename="somefile")
        l = l.req()
        l.prepare()
        eq_(l.modname, __name__)

    def testAutoModnameInject(self):
        l = twr.Link(filename="somefile")
        l.inject()
        local = tw2.core.core.request_local()
        eq_(local['resources'][0].modname, __name__)

    def testDirLink(self):
        dl = twr.DirLink(modname="tw2.core", filename="somefile")
        i = dl.req()
        i.prepare()
        self.assert_(i.link)

    def testJSSource(self):
        import uuid
        token = str(uuid.uuid4())
        s = twr.JSSource(src=token)
        res = str(s.req())
        self.assert_(token in res, res)

    def testJSFuncCallChained(self):
        rl = testapi.request(1, mw)
        options = {'foo': 20}
        jQuery = twc.js_function('jQuery')

        when_ready = lambda func: twc.js_callback(
            '$(document).ready(function(){' + str(func) + '});'
        )

        class Dummy(twc.Widget):
            id = 'dummy'
            template = "tw2.core.test_templates.display_only_test_widget"

            def prepare(self):
                super(Dummy, self).prepare()
                self.add_call(when_ready(
                    jQuery('.%s' % self.id).buildMenu(options)
                ))

        output = Dummy.display()
        eq_(len(rl['resources']), 1)
        eq_(str(rl['resources'][0]), '$(document).ready(function(){jQuery(".dummy").buildMenu({"foo": 20})});')

    def testJSFuncCallDictArgs(self):
        args = dict(foo="foo", bar="bar")
        function = "jquery"
        s = twr._JSFuncCall(function=function, args=args).req()
        s.prepare()
        self.assert_(function in str(s))
        for k in args:
            self.assert_("\"%s\": " % k in str(s))

        self.assert_(hash(s))
        s.args = [1, 2, 3]
        self.assert_(hash(s))
        s.args = None
        self.assert_(hash(s))
        self.assert_(s == s)


if __name__ == '__main__':
    unittest.main()
