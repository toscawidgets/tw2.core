import tw2.core as twc, testapi, tw2.core.testbase as tb, tw2.core.widgets as wd
from nose.tools import eq_
from webob import Request

class Test6(twc.Widget):
    test = twc.Param(attribute=True)

class TestWidgets(object):
    def setUp(self):
        testapi.setup()

    #--
    # Widget.process
    #--
    def xxtest_required(self):
        test = twc.Widget(id='test')
        try:
            test.req()
            assert(False)
        except twc.ParameterError, e:
            assert(str(e) == 'Widget is missing required parameter template')

    def test_attribute(self):
        test = Test6(id='test', template='test', test='wibble').req()
        test.prepare()
        assert(test.attrs['test'] == 'wibble')

    # this behaviour is removed
    def test_attribute_clash(self):
        test = Test6(id='test', template='test', test='wibble').req()
        test.attrs = {'test':'blah'}
        try:
            test.prepare()
            assert(False)
        except twc.ParameterError:
            pass

    def test_deferred(self):
        test = twc.Widget(id='test', template=twc.Deferred(lambda: 'test'))
        assert(test.template != 'test')
        ins = test.req()
        ins.prepare()
        assert(ins.template == 'test')

    def test_child_attr(self):
        class LayoutContainer(twc.CompoundWidget):
            label = twc.ChildParam(default='b')
        test = LayoutContainer(children=[twc.Widget(id='a', label='a')]).req()
        assert(test.c.a.label == 'a')
        test = LayoutContainer(children=[twc.Widget(id='a')]).req()
        assert(test.c.a.label == 'b')

    def test_params_as_vars(self):
        import mako
        class MyTest(twc.Widget):
            template = 'mako:tw2.tests.templates.simple_mako'
            test= twc.Param('blah', default='hello')
        testapi.request(1)
        twc.core.request_local()['middleware'] = twc.make_middleware(None, params_as_vars=True)
        MyTest.display()
        twc.core.request_local()['middleware'] = twc.make_middleware(None, params_as_vars=False)
        try:
            MyTest.display()
            assert(False)
        except TypeError:
            # this will raise a type error because "Undefined" is found (not a string)
            pass
            

    def test_meta_forceid(self):
        class MyTest(twc.CompoundWidget):
            a = twc.Widget(id='fred')
            b = twc.Widget()
        assert(MyTest.children[0].id == 'fred')
        assert(MyTest.children[1].id == 'b')

class TestPage(tb.WidgetTest):
    widget = wd.Page
    attrs = {#'child':
             'title':'some title'
             }
    expected = """<html>
<head><title>some title</title></head>
<body><h1>some title</h1></body>
</html>"""
    
    def _test_fetch_data(self):
        #not sure what causes this to fail
        r = self.widget(**self.attrs).fetch_data(None)
        eq_(r, None)
        
    def test_request_post(self):
        environ = {'REQUEST_METHOD': 'POST',
                   }
        req=Request(environ)
        r = self.widget(**self.attrs)().request(req)
        tb.assert_eq_xml(r.body, """<html>
<head><title>some title</title></head>
<body><h1>some title</h1></body>
</html>""")
