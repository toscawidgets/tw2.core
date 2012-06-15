import tw2.core as twc
import testapi
import itertools
import os
import webob as wo
from nose.tools import raises, eq_
from strainer.operators import assert_eq_xhtml

# TBD: only test engines that are installed
engines = ['genshi', 'mako', 'jinja', 'kajiki', 'chameleon']


# Python 2.5 support shim.  TODO -- remove this in the future.
if not hasattr(itertools, 'product'):
    def product(*args):
        if not args:
            return iter(((),))  # yield tuple()
        return (items + (item,)
                for items in product(*args[:-1]) for item in args[-1])

    itertools.product = product


class TestWD(twc.Widget):
    test = twc.Param(default='bob')


class TestTemplate(object):
    def setUp(self):
        testapi.setup()


    def _check_render(self, template, data, expected, engine=None):
        if engine:
            mw = twc.make_middleware(None, preferred_rendering_engines=[engine])
            testapi.request(1, mw)
            twc.util.flush_memoization()

        out = twc.templating.render(template, 'string', data)
        assert(isinstance(out, unicode))
        eq_(out, expected)

    def test_get_source_inline(self):
        template_in = "awesome"
        template_out = twc.templating.get_source("mako", template_in, True)
        eq_(template_in, template_out)

    def test_get_source_mako(self):
        expected = "<p>TEST mako</p>"
        t = twc.templating.get_source("mako", "tw2.core.test_templates.simple")
        eq_(expected, t)

    def test_auto_select_engine(self):
        for engine in engines:
            #set up the default renderers
            yield self._check_render, 'tw2.core.test_templates.simple', {'test':engine}, '<p>TEST %s</p>'%engine, engine

    @raises(ValueError)
    def test_auto_select_unavailable_engine(self):
        engine = 'mako'
        self._check_render('tw2.core.test_templates.simple_genshi', {'test':engine}, '<p>TEST %s</p>'%engine, engine)

    def test_auto_select_cache_works(self):
        engine='genshi'
        args = 'tw2.core.test_templates.simple_genshi', 'string', {'test':engine}
        out = twc.templating.render(*args)
        assert(isinstance(out, unicode))
        assert out == '<p>TEST genshi</p>', out
        out = twc.templating.render(*args)
        assert(isinstance(out, unicode))
        assert out == '<p>TEST genshi</p>', out

    def test_auto_select_unavailable_engine_not_strict(self):
        engine = 'mako'
        mw = twc.make_middleware(
            None,
            preferred_rendering_engines=[engine],
            strict_engine_selection=False,
        )
        testapi.request(501, mw)
        self._check_render(
            'tw2.core.test_templates.simple_genshi',
            {'test':'blah!'},
            '<p>TEST blah!</p>',
        )

    def test_engines(self):
        for engine in engines:
            print "Testing %s..." % engine
            args = [
                '%s:tw2.core.test_templates.simple_%s' % (engine, engine),
                'string',
                {'test':'test1'},
            ]
            out = twc.templating.render(*args)
            assert(isinstance(out, unicode))
            assert(out == '<p>TEST test1</p>')

    def test_engines_unicode(self):
        for engine in engines:
            print "Testing %s..." % engine
            out = twc.templating.render(
                '%s:tw2.core.test_templates.simple_%s' % (engine, engine),
                'string', {'test':'test\u1234'}
            )
            assert(out == '<p>TEST test\u1234</p>')

    def test_nesting(self):
        "Check that templates can be correctly nested, in any combination"
        for outer, inner in itertools.product(engines, engines):
            print 'Testing %s on %s' % (inner, outer)
            test = twc.templating.render(
                '%s:tw2.core.test_templates.simple_%s' % (inner, inner),
                outer,
                {'test':'test1'},
            )
            out = twc.templating.render(
                '%s:tw2.core.test_templates.simple_%s' % (outer, outer),
                'string',
                {'test':test},
            )
            eq_(out, '<p>TEST <p>TEST test1</p></p>')

    def test_widget_display(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)
        mtest = TestWD(id='x')
        for eng in engines:
            test = mtest.req()
            test.template = '%s:tw2.core.test_templates.inner_%s' % (eng, eng)
            out = test.display()
            eq_(out, '<p>TEST bob</p>')

    def test_widget_nesting(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)
        for outer, inner in itertools.product(engines, engines):
            outer = '%s:tw2.core.test_templates.widget_%s' % (outer, outer)
            inner = '%s:tw2.core.test_templates.inner_%s' % (inner, inner)
            test = twc.CompoundWidget(
                id='x', template=outer,
                children=[TestWD(id='y', template=inner)]
            )
            eq_(test.display(), '<p>TEST <p>TEST bob</p></p>')

    def test_widget_relative_inheritance(self):
        twc.core.request_local()['middleware'] = twc.make_middleware(None)

        # These aren't yet supported in the tests yet.
        ignored_engines = ['jinja', 'kajiki', 'chameleon']

        for engine in engines:
            if engine in ignored_engines:
                continue
            template = "%s:tw2.core.test_templates.child_%s" % (engine, engine)
            test = twc.Widget(id='x', template=template)
            expected = """
            <html>
                <head><title>Parent</title></head>
                <body>Child</body>
            </html>
            """
            assert_eq_xhtml(test.display(), expected)

    def test_genshi_abs(self):
        test_dir = os.path.sep.join(__file__.split(os.path.sep)[:-1])
        fname = os.path.sep.join([test_dir, 'test.html'])
        twc.Widget(template='genshi_abs:%s' % fname).display()

    def test_genshi_relative_filename(self):
        """ Issue #30 -- http://bit.ly/LT4rBP """
        twc.Widget(template='genshi:./tests/test.html').display()

    def test_rendering_extension_propagation(self):
        mw = twc.make_middleware(None, preferred_rendering_engines=['genshi', 'jinja'],
                                       rendering_extension_lookup={'genshi':['genshi', 'html'],
                                                                   'jinja':['jinja']})
        assert twc.templating.get_engine_name('tw2.core.test_templates.parent_genshi', mw) == 'genshi'

        #flush caches to avoid wrong results due to cached results
        twc.util.flush_memoization()
        twc.templating.engine_name_cache = {}

        mw = twc.make_middleware(None, preferred_rendering_engines=['genshi', 'jinja'],
                                       rendering_extension_lookup={'genshi':['genshi'],
                                                                   'jinja':['jinja', 'html']})
        assert twc.templating.get_engine_name('tw2.core.test_templates.parent_genshi', mw) == 'jinja'
