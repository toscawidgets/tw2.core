import tw2.core as twc, testapi
from tw2.core import encoder, js_symbol, js_function, js_callback

from nose.tools import eq_

class TestJS(object):
    def setUp(self):
        testapi.setup()
        self.twe = encoder # Use TW2 encoder
        self.encode = self.twe.encode
        mw = twc.make_middleware(lambda *args, **kw: "I'm an app, lol!")
        testapi.request(1, mw=mw)

    # Deprecated Test
    #def test_js_function(self):
    #    obj = self.encode({"onLoad": js_function("do_something")("param")})
    #    assert obj == '{"onLoad": do_something(\\"param\\")}'

    def test_js_symbol(self):
        obj = self.encode({"onLoad": js_symbol("param")})
        eq_(obj, '{"onLoad": param}')

    # Deprecated Test
    #def test_mark_for_escape(self):
    #    obj = 'MyObject'
    #    assert self.twe.mark_for_escape(obj) == '*#*MyObject*#*'

    # Deprecated Test
    #def test_unescape_marked(self):
    #    obj = '"*#*MyObject*#*"'
    #    assert self.twe.unescape_marked(obj) == 'MyObject'

    def test_js_callback(self):
        eq_(str(js_callback("update_div")), 'update_div')
        eq_(str(js_callback(js_function('foo')(1,2,3))), 'function(){foo(1, 2, 3)}')

    def test_jsonified_js_function(self):
        obj = {
            'f': js_function("$.awesome")
        }
        json = self.encode(obj)
        eq_(json, '{"f": $.awesome}')
