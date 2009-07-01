import tw2.core as twc, testapi

# TBD: only test engines that are installed
engines = ['cheetah', 'kid', 'genshi', 'mako']

kid_prefix = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n"""
def strip_prefix(prefix, s):
    return s[len(prefix):] if isinstance(s, basestring) and s.startswith(prefix) else s

class TestWD(twc.Widget):
    test = twc.Param(default='bob')


class TestTemplate(object):
    def setUp(self):
        testapi.setup()

    def test_engines(self):
        for engine in engines:
            print "Testing %s..." % engine
            out = twc.template.EngineManager().render('%s:tw2.tests.templates.simple_%s' % (engine, engine), 'string', {'test':'test1'})
            out = strip_prefix(kid_prefix, out)
            assert(isinstance(out, unicode))
            assert(out == '<p>TEST test1</p>')

    def test_engines_unicode(self):
        for engine in engines:
            print "Testing %s..." % engine
            out = twc.template.EngineManager().render('%s:tw2.tests.templates.simple_%s' % (engine, engine), 'string', {'test':'test\u1234'})
            out = strip_prefix(kid_prefix, out)
            assert(out == '<p>TEST test\u1234</p>')

    def test_engine_dupe(self):
        em = twc.template.EngineManager()
        t = em[engines[0]]
        try:
            em.load_engine(engines[0])
            assert(False)
        except twc.EngineError, e:
            assert(str(e) == "Template engine '%s' is already loaded" % engines[0])

    def test_engine_notfound(self):
        try:
            t = twc.template.EngineManager()['fred']
            assert(False)
        except twc.EngineError, e:
            assert(str(e) == "No template engine available for 'fred'")

    def test_extra_vars(self):
        eng = twc.template.EngineManager()
        for engine in engines:
            print "Testing %s..." % engine
            eng.load_engine(engine, extra_vars_func=lambda: {'test':'wobble'})
            out = eng.render('%s:tw2.tests.templates.simple_%s' % (engine, engine), 'string', {})
            out = strip_prefix(kid_prefix, out)
            assert(out == '<p>TEST wobble</p>')

    def test_nesting(self):
        "Check that templates can be correctly nested, in any combination"
        eng = twc.template.EngineManager()
        for outer in engines:
            for inner in engines:
                print 'Testing %s on %s' % (inner, outer)
                test = eng.render('%s:tw2.tests.templates.simple_%s' % (inner, inner), outer, {'test':'test1'})
                test = strip_prefix(kid_prefix, test)
                out = eng.render('%s:tw2.tests.templates.simple_%s' % (outer, outer), 'string', {'test':test})
                out = strip_prefix(kid_prefix, out)
                print out
                assert(out == '<p>TEST <p>TEST test1</p></p>')

    def test_widget_display(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)
        mtest = TestWD(id='x')
        for eng in engines:
            test = mtest.req()
            test.template = '%s:tw2.tests.templates.inner_%s' % (eng, eng)
            out = strip_prefix(kid_prefix, test.display())
            assert(out == '<p>TEST bob</p>')

    def test_widget_nesting(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)
        for outer in engines:
            for inner in engines:
                test = twc.CompoundWidget(id='x',
                    template = '%s:tw2.tests.templates.widget_%s' % (outer, outer),
                    children=[
                        TestWD(id='y', template='%s:tw2.tests.templates.inner_%s' % (inner, inner)),
                    ]
                )
                assert(test.display().replace(kid_prefix, '') == '<p>TEST <p>TEST bob</p></p>')
