import tw2.core as twc, testapi
from tw2.core import TWEncoder, js_symbol, js_function, js_callback, encode


class TestJS(object):
    def setUp(self):
        testapi.setup()
        self.twe = TWEncoder()
        self.encode = self.twe.encode

    def test_js_function(self):
        obj = self.encode({"onLoad": js_function("do_something")("param")})
        assert obj == '{"onLoad": do_something(\\"param\\")}'

    def test_js_symbol(self):
        obj = self.encode({"onLoad": js_symbol("param")})
        assert obj == '{"onLoad": param}'

    def test_mark_for_escape(self):
        obj = 'MyObject'
        assert self.twe.mark_for_escape(obj) == '*#*MyObject*#*'

    def test_unescape_marked(self):
        obj = '"*#*MyObject*#*"'
        assert self.twe.unescape_marked(obj) == 'MyObject'

    def test_js_callback(self):
        assert str(js_callback("update_div")) == 'update_div'
        assert str(js_callback(js_function('foo')(1,2,3))) == 'function(){foo(1, 2, 3)}'
