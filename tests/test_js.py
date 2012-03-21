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

    def test_js_function(self):
        json = self.encode({"onLoad": js_function("do_something")("param")})
        eq_(json, '{"onLoad": do_something(\\"param\\")}')

    def test_js_function_composition(self):
        f = js_function("f")
        g = js_function("g")
        h = js_function("h")

        y = js_symbol("y")

        obj = f(g(h("x", y)))

        eq_(str(obj), """f(g(h("x", y)))""")

    def test_js_symbol(self):
        obj = self.encode({"onLoad": js_symbol("param")})
        eq_(obj, '{"onLoad": param}')

    def test_js_callback(self):
        eq_(str(js_callback("update_div")), 'update_div')
        eq_(str(js_callback(js_function('foo')(1,2,3))), 'function(){foo(1, 2, 3)}')

    def test_jsonified_js_function(self):
        obj = {
            'f': js_function("$.awesome")
        }
        json = self.encode(obj)
        eq_(json, '{"f": $.awesome}')

    def test_encoding_widget_id(self):
        from tw2.core import Widget
        w = Widget("foo")

        f = js_callback(js_function('jQuery')(w).click(js_symbol('onClick')))
        args = {'onLoad': f}

        json = self.encode(args)
        eq_(json, '{"onLoad": function(){jQuery(\\"foo\\").click(onClick)}}')

        json = self.encode({'args':args})
        eq_(json, '{"args": {"onLoad": function(){jQuery(\\"foo\\").click(onClick)}}}')
