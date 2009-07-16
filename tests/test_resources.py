import webob as wo, webtest as wt, tw2.core as twc, tw2.tests, os, testapi, tw2.core.resources as twr, tw2.core.testbase as tb, tw2.core.params as pm
from nose.tools import eq_, raises

js = twc.JSLink(link='paj')
css = twc.CSSLink(link='joe')
jssrc = twc.JSSource(src='bob')

TestWidget = twc.Widget(template='genshi:tw2.tests.templates.inner_genshi', test='test')
html = "<html><head><title>a</title></head><body>hello</body></html>"

inject_widget = TestWidget(id='a', resources=[js])

def simple_app(environ, start_response):
    req = wo.Request(environ)
    ct = 'text/html' if req.path == '/' else 'test/plain'
    resp = wo.Response(request=req, content_type="%s; charset=UTF8" % ct)
    inject_widget.display()
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
        wb = TestWidget(id='b', resources=[js,css])
        wa.display()
        rl = twc.core.request_local()
        assert(len(rl.get('resources', [])) == 0)
        wb.display()
        for r in rl['resources']:
            assert(any(isinstance(r, b) for b in [js,css]))
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


    #--
    # ResourcesApp
    #--
    def test_not_found(self):
        #assert(tst_mw.get('/fred', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/test', expect_errors=True).status == '404 Not Found')

    def test_serve(self):
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        fcont = open(os.path.join(os.path.dirname(tw2.tests.__file__), 'templates/simple_genshi.html')).read()
        assert(tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body == fcont)
        assert(tst_mw.get('/resources/tw2.tests/templates/notexist', expect_errors=True).status == '404 Not Found')

    def test_different_file(self):
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        assert(tst_mw.get('/resources/tw2.tests/simple_kid.kid', expect_errors=True).status == '404 Not Found')

    def test_whole_dir(self):
        mw.resources.register('tw2.tests', 'templates/', whole_dir=True)
        fcont = open(os.path.join(os.path.dirname(tw2.tests.__file__), 'templates/simple_genshi.html')).read()
        assert(tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body == fcont)
        assert(tst_mw.get('/resources/tw2.tests/templates/notexist', expect_errors=True).status == '404 Not Found')

    def test_dir_traversal(self): # check for potential security flaw
        mw.resources.register('tw2.tests', 'templates/')
        assert(tst_mw.get('/resources/tw2.tests/__init__.py', expect_errors=True).status == '404 Not Found')
        assert(tst_mw.get('/resources/tw2.tests/templates/../__init__.py', expect_errors=True).status == '404 Not Found')

    def test_zipped(self):
        # assumes webtest is installed as a zipped egg
        mw.resources.register('webtest', '__init__.py')
        assert(tst_mw.get('/resources/webtest/__init__.py').body.startswith('# (c) 2005 Ian'))

    def test_cache_header(self):
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        cache = tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').headers['Cache-Control']
        assert(cache == 'max_age=3600')

    #--
    # Links register resources
    #--
    def test_link_reg(self):
        testapi.request(1, mw)
        wa = twc.JSLink(modname='tw2.tests', filename='templates/simple_mako.mak').req()
        wa.prepare()
        assert(wa.link == '/resources/tw2.tests/templates/simple_mako.mak')
        tst_mw.get(wa.link)

    def test_mime_type(self):
        testapi.request(1, mw)
        wa = twc.JSLink(modname='tw2.tests', filename='templates/simple_genshi.html').req()
        wa.prepare()
        resp = tst_mw.get(wa.link)
        assert(resp.content_type == 'text/html')
        assert(resp.charset == 'UTF-8')

    #--
    # Resource injector
    #--
    def test_inject_head(self):
        rl = testapi.request(1, mw)
        out = twc.inject_resources(html, [js.req()])
        assert(out == '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello</body></html>')

    def test_inject_body(self):
        rl = testapi.request(1, mw)
        out = twc.inject_resources(html, [jssrc.req()])
        assert(out == '<html><head><title>a</title></head><body>hello<script type="text/javascript">bob</script></body></html>')

    def test_inject_both(self):
        rl = testapi.request(1, mw)
        out = twc.inject_resources(html, [js.req(), jssrc.req()])
        assert(out == '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello<script type="text/javascript">bob</script></body></html>')

    def test_detect_clear(self):
        widget = twc.Widget(id='a', template='genshi:tw2.tests.templates.inner_genshi', test='test', resources=[js])
        rl = testapi.request(1, mw)
        eq_(rl.get('resources', []), [])
        widget.display()
        rl = twc.core.request_local()
        assert(len(rl.get('resources', [])) == 1)
        out = twc.inject_resources(html)
        print 'after inject_res'
        print rl
        eq_(rl.get('resources', []), [])

    #--
    # General middleware
    #--
    def test_mw_resourcesapp(self):
        testapi.request(1)
        mw.resources.register('tw2.tests', 'templates/simple_genshi.html')
        fcont = open(os.path.join(os.path.dirname(tw2.tests.__file__), 'templates/simple_genshi.html')).read()
#        print tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body
        assert(tst_mw.get('/resources/tw2.tests/templates/simple_genshi.html').body == fcont)

    def test_mw_clear_rl(self):
        rl = testapi.request(1)
        rl['blah'] = 'lah'
        tst_mw.get('/')
        rl = twc.core.request_local()
        assert(rl == {})

    def test_mw_inject(self):
        testapi.request(1, mw)
        eq_(tst_mw.get('/').body, '<html><head><script type="text/javascript" src="paj"></script><title>a</title></head><body>hello</body></html>')

    def test_mw_inject_html_only(self):
        testapi.request(1, mw)
        assert(tst_mw.get('/plain').body == html)

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
    expected = '<link rel="stylesheet" type="text/css" href="something" media="all">'


class TestJsSource(tb.WidgetTest):
    widget = twr.JSSource
    attrs = {'src':'something'}
    expected = '<script type="text/javascript">something</script>'

    def _test_repr_(self):
        #not sure how to test resources.py:79
        r = repr(self.widget(**self.attrs))
        assert r == "<class 'tw2.core.params.JSSource_s'>", r


class TestJsFuncall(tb.WidgetTest):
    widget = twr.JSFuncCall
    attrs = {'function':'foo', 'args':['a', 'b']}
    expected = None

    def test_display(self):
        r = self.widget(**self.attrs).display(**self.params)
        assert r == """<script type="text/javascript">foo("a", "b")</script>""", r

from pkg_resources import Requirement
class TestResourcesApp:

    def setup(self):
        class Config(object):pass
        config = Config()
        config.res_prefix = ""
        self.app = twr.ResourcesApp(config)

    def test_register_requirement(self):
        req = Requirement.parse('tw2.core>1.0')
        self.app.register(req, 'something.txt')

def test_find_charset():
    eq_(twc.resources.find_charset('charset=iso-8859-1'), 'iso-8859-1')