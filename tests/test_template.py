import tw2.core as twc, testapi
import webob as wo
import os
from nose.tools import raises, eq_

# TBD: only test engines that are installed
engines = ['genshi', 'mako']


class TestWD(twc.Widget):
    test = twc.Param(default='bob')

class TestTemplate(object):
    def setUp(self):
        testapi.setup()

    def _check_render(self, template, data, expected, engine=None):
        if engine:
            mw = twc.make_middleware(None, preferred_rendering_engines=[engine])
            testapi.request(1, mw)
        out = twc.template.EngineManager().render(template, 'string', data)
        assert(isinstance(out, unicode))
        assert out == expected, out

    def test_auto_select_engine(self):
        for engine in engines:
            #set up the default renderers
            yield self._check_render, 'tw2.core.test_templates.simple', {'test':engine}, '<p>TEST %s</p>'%engine, engine

    @raises(twc.template.EngineError)
    def test_auto_select_unavailable_engine(self):
        engine = 'mako'
        self._check_render('tw2.core.test_templates.simple_genshi', {'test':engine}, '<p>TEST %s</p>'%engine, engine)

    def test_auto_select_cache_works(self):
        engine='genshi'
        args = 'tw2.core.test_templates.simple_genshi', 'string', {'test':engine}
        em = twc.template.EngineManager()
        out = em.render(*args)
        assert(isinstance(out, unicode))
        assert out == '<p>TEST genshi</p>', out
        out = em.render(*args)
        assert(isinstance(out, unicode))
        assert out == '<p>TEST genshi</p>', out

    def test_auto_select_unavailable_engine_not_strict(self):
        engine = 'mako'
        mw = twc.make_middleware(None, preferred_rendering_engines=[engine], strict_engine_selection=False)
        testapi.request(501, mw)
        self._check_render('tw2.core.test_templates.simple_genshi', {'test':'blah!'}, '<p>TEST blah!</p>')

    def test_engines(self):
        for engine in engines:
            print "Testing %s..." % engine
            out = twc.template.EngineManager().render('%s:tw2.core.test_templates.simple_%s' % (engine, engine), 'string', {'test':'test1'})
            assert(isinstance(out, unicode))
            assert(out == '<p>TEST test1</p>')

    def test_engines_unicode(self):
        for engine in engines:
            print "Testing %s..." % engine
            out = twc.template.EngineManager().render('%s:tw2.core.test_templates.simple_%s' % (engine, engine), 'string', {'test':'test\u1234'})
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
            eq_(str(e), "No template engine for 'fred'")

    def test_extra_vars(self):
        eng = twc.template.EngineManager()
        for engine in engines:
            # mako is exempt
            if engine == 'mako':
                continue
            print "Testing %s..." % engine
            eng.load_engine(engine, extra_vars_func=lambda: {'test':'wobble'})
            out = eng.render('%s:tw2.core.test_templates.simple_%s' % (engine, engine), 'string', {})
            assert(out == '<p>TEST wobble</p>')

    def test_nesting(self):
        "Check that templates can be correctly nested, in any combination"
        eng = twc.template.EngineManager()
        for outer in engines:
            for inner in engines:
                print 'Testing %s on %s' % (inner, outer)
                test = eng.render('%s:tw2.core.test_templates.simple_%s' % (inner, inner), outer, {'test':'test1'})
                out = eng.render('%s:tw2.core.test_templates.simple_%s' % (outer, outer), 'string', {'test':test})
                print out
                assert(out == '<p>TEST <p>TEST test1</p></p>')

    def test_widget_display(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)
        mtest = TestWD(id='x')
        for eng in engines:
            print eng
            test = mtest.req()
            test.template = '%s:tw2.core.test_templates.inner_%s' % (eng, eng)
            out = test.display()
            assert(out == '<p>TEST bob</p>')

    def test_widget_nesting(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)
        for outer in engines:
            for inner in engines:
                test = twc.CompoundWidget(id='x',
                    template = '%s:tw2.core.test_templates.widget_%s' % (outer, outer),
                    children=[
                        TestWD(id='y', template='%s:tw2.core.test_templates.inner_%s' % (inner, inner)),
                    ]
                )
                assert(test.display() == '<p>TEST <p>TEST bob</p></p>')

    def test_genshi_abs(self):
        test_dir = os.path.sep.join(__file__.split(os.path.sep)[:-1])
        fname = os.path.sep.join([test_dir, 'test.html'])
        twc.Widget(template='genshi_abs:%s' % fname).display()
