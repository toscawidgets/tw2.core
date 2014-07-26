
from unittest import TestCase
from nose.tools import eq_, raises
from webob import Request
from sieve.operators import (
    eq_xml as eq_xhtml,
    assert_eq_xml as assert_eq_xhtml,
)

import tw2.core as twc, testapi, tw2.core.testbase as tb
import tw2.core.widgets as wd, tw2.core.validation as vd, tw2.core.params as pm
import six


class Test6(twc.Widget):
    test = twc.Param(attribute=True)

class TestWidgets(object):
    def setUp(self):
        testapi.setup()

    #--
    # Widget.process
    #--
    def test_backwards_compat_new(self):
        """ Ticket #4 `.__init__(id, ...)` """
        test = twc.Widget('test')
        eq_(test.id, 'test')

    def test_backwards_compat_display(self):
        """ Ticket #4 `.display(value, ...)` """
        test = twc.Widget(
            id='test',
            template="genshi:tw2.core.test_templates.field_genshi"
        )
        output = test.display("foo")
        eq_(output, six.u('<p>foo </p>'))

    def test_inline_template(self):
        """ Ticket #69 """
        test = twc.Widget(
            id='test',
            template="<p>${w.value} </p>",
            inline_engine_name="mako",
        )
        output = test.display("foo")
        eq_(output, six.u('<p>foo </p>'))

    def test_inline_template_with_no_markup(self):
        """ Ticket #69 """
        test = twc.Widget(
            id='test',
            template="${w.value}",
            inline_engine_name="mako",
        )
        output = test.display("foo")
        eq_(output, six.u('foo'))

    def xxtest_required(self):
        test = twc.Widget(id='test')
        try:
            test.req()
            assert(False)
        except twc.ParameterError as e:
            assert(str(e) == 'Widget is missing required parameter template')

    def test_attribute(self):
        test = Test6(id='test', template='test', test='wibble').req()
        test.prepare()
        assert(test.attrs['test'] == 'wibble')

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

    def test_deferred_value_no_subclass(self):
        test = twc.Widget(id='test',
                          template="<p>${w.value}</p>",
                          inline_engine_name="mako",
                          value=twc.Deferred(lambda: 'test'))
        assert(test.value != 'test')
        ins = test.req()
        ins.prepare()
        assert(ins.value == 'test')
        assert(test.display() == "<p>test</p>")

    def test_deferred_value_subclass_with_display(self):
        class TestWidget(twc.Widget):
            id='test'
            inline_engine_name = 'mako'
            template = "<p>${w.value}</p>"
            value=twc.Param()

        test = TestWidget

        eq_(test.display(value="test"), "<p>test</p>")
        eq_(test.display(value=twc.Deferred(lambda: 'test')), "<p>test</p>")

    def test_deferred_value_subclass(self):
        class TestWidget(twc.Widget):
            id='test'
            inline_engine_name = 'mako'
            template = "<p>${w.value}</p>"
            value=twc.Param(attribute=True)

        test = TestWidget
        expected = "<p>test</p>"
        # This should be fine
        eq_(test(value=twc.Deferred(lambda: 'test')).display(), expected)
        # This one is more tricky.
        eq_(test(value=twc.Deferred(lambda: 'test'))().display(), expected)

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
            template = 'mako:tw2.core.test_templates.simple_mako'
            test= twc.Param('blah', default='hello')
        testapi.request(1)
        twc.core.request_local()['middleware'] = twc.make_middleware(None, params_as_vars=True)
        MyTest.display()
        twc.core.request_local()['middleware'] = twc.make_middleware(None, params_as_vars=False)
        try:
            MyTest.display()
            assert(False)
        except NameError:
            # this will raise a name error because "Undefined"
            # is found (not a string)
            pass


    def test_meta_forceid(self):
        class MyTest(twc.CompoundWidget):
            a = twc.Widget(id='fred')
            b = twc.Widget()
        eq_(MyTest.children[0].id, 'fred')
        eq_(MyTest.children[1].id, 'b')

class TestRepeatingWidgetBunchCls():

    def setup(self):
        self.bunch = wd.RepeatingWidgetBunchCls('')

    @raises(KeyError)
    def test_bad_getitem(self):
        self.bunch['asdf']

class TestRepeatingWidgetBunch():

    def setup(self):
        self.bunch = wd.RepeatingWidgetBunch('', '')

    @raises(KeyError)
    def test_bad_getitem(self):
        self.bunch['asdf']

class AlwaysValidateFalseValidator(vd.Validator):
    def _validate_python(self, params, state=None):
        raise vd.ValidationError('I always throw up on roller coasters.')
class AlwaysValidateFalseWidget(wd.Widget):
    validator = AlwaysValidateFalseValidator()
    template = "mako:tw2.core.test_templates.always_validate_false_widget"

class CompoundTestWidget(wd.CompoundWidget):
    children = [AlwaysValidateFalseWidget(id="something"),]

class TWidget(wd.Widget):
    template = "mako:tw2.core.test_templates.display_only_test_widget"

class TestWidget(tb.WidgetTest):
    widget = TWidget
    attrs = {'id':"w", 'validator':AlwaysValidateFalseValidator}
    expected = """<p>Test Widget</p>"""
    validate_params = [[None, {'w':''}, None, vd.ValidationError],[None, {}, None, vd.ValidationError]]

    def test_fe_validator(self):
        class FEWidget(wd.Widget):
            if vd.formencode:
                validator = vd.formencode.validators.Int()
            else:
                validator = vd.IntValidator()
        FEWidget(id="s").validate({'s':'3'})

    @raises(twc.WidgetError)
    def test_only_parent_validation(self):
        CompoundTestWidget().children[0].validate({})

    def _test_safe_modify(self):
        # i am stumped on this one
        # widgets.py:250-252
        w = self.widget()
        w.safe_parameter = {'a':1}
        w.safe_modify(w, 'safe_parameter')

    def _test_request_local_validated_widget(self):
        # this seems like it's on the right track, but i dunno, it Seg. Faults
        # widgets.py:193
        rl = twc.core.request_local()
        rl['validated_widget'] = TWidget()
        self.widget().display()

    @raises(pm.ParameterError)
    def test_bad_validator(self):
        class MWidget(wd.Widget):
            validator = 'asdf'
        MWidget()

    def test_required_vd(self):
        class MWidget(wd.Widget):
            validator = pm.Required
        MWidget()

class SubCompoundTestWidget(wd.CompoundWidget):
    children = [CompoundTestWidget()]

class TestWidgetNoneBug(tb.WidgetTest):
    widget = wd.Widget(template='genshi:tw2.core.test_templates.field_genshi')
    attrs = {'validator':twc.IntValidator}
    params = {'value':None}
    expected = '<p> </p>'


def test_arguments_to_display_as_class_method():
    """ As of Issue #41, this passes. """

    class TestWidget(twc.Widget):
        template = "<p>${w.value}</p>"
        inline_engine_name = "mako"
        value = twc.Param()

    eq_(TestWidget.display(value="test"), "<p>test</p>")


def test_arguments_to_display_as_instance_method():
    """ As of Issue #41, this fails. """

    class TestWidget(twc.Widget):
        template = "<p>${w.value}</p>"
        inline_engine_name = "mako"
        value = twc.Param()

    ins = TestWidget.req()
    eq_(ins.display(value="test"), "<p>test</p>")


class TestSubCompoundWidget(tb.WidgetTest):
    widget = SubCompoundTestWidget
    attrs = {'id':"rw", 'repetitions':1, 'validator':AlwaysValidateFalseValidator}
    expected = """<div id="rw"><div><p>Test Widget</p></div></div>"""
    validate_params = [[None, {'rw':''}, None, vd.ValidationError]]

    def test_string_value(self):
        w = self.widget(**self.attrs)()
        w.value = "value"
        r = w.display("value")
        assert_eq_xhtml(r, self.expected)

    @raises(twc.WidgetError)
    def test_duplicate_ids(self):
        class CompoundTestWidget(wd.CompoundWidget):
            children = [AlwaysValidateFalseWidget(id="something"), AlwaysValidateFalseWidget(id="something")]
        CompoundTestWidget()

    @raises(pm.ParameterError)
    def test_child_not_widget(self):
        class CompoundTestWidget(wd.CompoundWidget):
            children = ["", AlwaysValidateFalseWidget(id="something")]
        CompoundTestWidget()

class TestCompoundWidget(tb.WidgetTest):
    widget = CompoundTestWidget
    attrs = {'id':"rw", 'repetitions':1, 'validator':AlwaysValidateFalseValidator}
    expected = """<div id="rw"><p>Test Widget</p></div>"""
    validate_params = [[None, {'rw':''}, None, vd.ValidationError], [None, {'rw':'asdf'}, None, vd.ValidationError]]

class RepeatingTestWidget(wd.RepeatingWidget):
    child = AlwaysValidateFalseWidget

class TestRepeatingTestWidget(tb.WidgetTest):
    widget = RepeatingTestWidget
    attrs = {'id':"rw", 'repetitions':1, 'validator':AlwaysValidateFalseValidator}
    expected = """<div id="rw"><p>Test Widget</p></div>"""
    validate_params = [[None, {'rw':''}, None, vd.ValidationError]]

    @raises(pm.ParameterError)
    def test_child_must_have_no_id(self):
        class DummyRepeatingTestWidget(wd.RepeatingWidget):
            child = AlwaysValidateFalseWidget(id="something")
        DummyRepeatingTestWidget()

    @raises(pm.ParameterError)
    def test_child_is_not_widget(self):
        class DummyRepeatingTestWidget(wd.RepeatingWidget):
            child = ""
        DummyRepeatingTestWidget()

    def test_class_with_children(self):
        class DummyWidget(wd.Widget): pass
        class DummyRepeatingTestWidget(wd.RepeatingWidget):
            child=DummyWidget()
            children=[DummyWidget()]
        w = DummyRepeatingTestWidget()

    def test_separator(self):
        widget = RepeatingTestWidget
        attrs = {
            'id': "rw",
            'repetitions': 3,
            'validator': AlwaysValidateFalseValidator,
            'separator': '<hr />'}
        params = {'separator': '<hr />'}
        expected = ('<div id="rw">'
                    '<p>Test Widget</p><hr />'
                    '<p>Test Widget</p><hr />'
                    '<p>Test Widget</p>'
                    '</div>')
        for engine in self._get_all_possible_engines():
            yield (self._check_rendering_vs_expected,
                engine, attrs, params, expected)

class DisplayOnlyTestWidget(wd.DisplayOnlyWidget):
    child = twc.Variable(default=AlwaysValidateFalseWidget)
    template = "mako:tw2.core.test_templates.display_only_test_widget"

class TestDisplayOnlyTestWidget(tb.WidgetTest):
    widget = DisplayOnlyTestWidget
    attrs = {'id':"dotw"}
    expected = """<p>Test Widget</p>"""
    validate_params = [[None, {'dotw':''}, None, vd.ValidationError]]

    @raises(pm.ParameterError)
    def test_post_init_fail(self):
        class DummyWidget(wd.Widget): pass
        class DummyDOTestWidget(wd.DisplayOnlyWidget):
            template = "mako:tw2.core.test_templates.display_only_test_widget"
            child=DummyWidget(id="lala")
        w = DummyDOTestWidget(id="something")

    @raises(pm.ParameterError)
    def test_childclass_not_widget_fail(self):
        class DummyWidget(wd.Widget): pass
        class DummyDOTestWidget(wd.DisplayOnlyWidget):
            template = "mako:tw2.core.test_templates.display_only_test_widget"
            child="something"
        w = DummyDOTestWidget(id="something")

    def test_class_with_children(self):
        class DummyWidget(wd.Widget): pass
        class DummyDOTestWidget(wd.DisplayOnlyWidget):
            template = "mako:tw2.core.test_templates.display_only_test_widget"
            child=DummyWidget(id="something")
            children=[DummyWidget(id="something_else")]
        w = DummyDOTestWidget(id="something")

class TestPage(tb.WidgetTest):
    widget = wd.Page
    attrs = {#'child':
             'title':'some title'
             }
    expected = """<html>
<head><title>some title</title></head>
<body><h1>some title</h1></body>
</html>"""

    def test_fetch_data(self):
        r = self.widget(**self.attrs).req().fetch_data(None)
        eq_(r, None)

    def test_request_post(self):
        environ = {'REQUEST_METHOD': 'POST',
                   }
        req=Request(environ)
        r = self.widget(_no_autoid=True, **self.attrs).request(req)
        assert_eq_xhtml(r.body, """<html>
<head><title>some title</title></head>
<body><h1>some title</h1></body>
</html>""")


class TestWidgetMisc(TestCase):
    def setUp(self):
        testapi.setup()

    def testCircularParent(self):
        """
        should raise WidgetError
        """
        class Child(wd.Widget):
            pass

        class Parent(wd.Widget):
            pass

        Parent.parent = Child(id="child")
        Parent.child = Parent
        Parent.child.parent = Parent
        try:
            Parent(id="loopy").compound_id
        except twc.WidgetError as we:
            self.assert_("loop" in str(we).lower(), str(we))
        else:
            self.assert_(False)

    def testCompoundIDForUrlRepeater(self):
        class Parent(wd.RepeatingWidget):
            pass

        class Child(wd.Widget):
            pass

        Child.parent = Parent
        wid = Child(id="forurl")._compound_id_elem(for_url=True)
        self.assert_(not wid)

    def testGetLinkNoID(self):
        try:
            wd.Widget.get_link()
            self.assert_(False)
        except twc.WidgetError:
            self.assert_(True)

    def testGetLinkID(self):
        from tw2.core.middleware import TwMiddleware
        mw = TwMiddleware(None)
        testapi.request(1, mw)

        class CWidget(wd.Widget):
            id="foo"

            @classmethod
            def request(cls, req):
                pass

        self.assert_(CWidget.get_link())

    def testValidationError(self):

        originalInvalid = vd.Invalid

        class MockInvalid(Exception):
            def __init__(self, msg):
                self.msg = msg
                super(MockInvalid, self).__init__(msg)

        vd.catch = MockInvalid  # patch Invalid for this test
        try:
            err_msg = "NO"

            class MockValidator(vd.Validator):
                def from_python(self, value, state=None):
                    raise MockInvalid(err_msg)

            class T(wd.Widget):
                validator = MockValidator()
                template = ""

            i = T.req()
            i.prepare()
            self.assert_(err_msg in i.error_msg)
        finally:
            vd.catch = originalInvalid  # reverse patch

    def testIterParams(self):
        class T(wd.Widget):
            template = "goo"
            foo = pm.Param(default="foo")
            bar = pm.Param(default="bar")

        i = T(id="testme").req()
        params = dict(i.iteritems())
        self.assert_("foo" in params)
        self.assert_("bar" in params)

    def testAddCall(self):

        class T(wd.Widget):
            test = twc.Param('blah', default='hello')
            template = 'mako:tw2.core.test_templates.simple_mako'

        i = T(id="foo").req()
        jscall = ["somefunc", "bodybottom"]
        i.add_call(jscall[0], jscall[1])
        self.assert_(jscall in i._js_calls)
        mw = twc.make_middleware(None, params_as_vars=True)
        testapi.request(1, mw)
        res = i.display(displays_on="string")
        self.assert_(res)
        self.assert_(i.resources)

    def testSafeModify(self):
        """
        this method isn't called anywhere in the code, so not sure
        whether it's dead code or not. also ... no docstring
        """
        class BT(wd.Widget):
            myresources = ["a"]

        class T(BT):
            pass

        i = T.req()
        self.assert_("myresources" not in i.__dict__)
        i.safe_modify("myresources")
        self.assert_("a" in i.myresources, i.myresources)

    def testGetChildErrorMsgs(self):
        """
        this code doesn't seem to be called anywhere, bare minimum for
        test coverage
        """
        class T(wd.CompoundWidget):
            error_msg ="child:child error"
            children = []
        i = T.req()
        self.assert_(i.get_child_error_message("child") == "child error")

    def testValidateKeyedChildren(self):
        """
        if children have a key attribute then values passed in by key
        will be routed to the children whose key. still returned as a
        dict by id though
        """
        class T(wd.CompoundWidget):
            children = [wd.Widget(id="ct", key="kct"),
                        wd.Widget(id="oct", key="koct")]

        i = T(id="test").req()
        self.assert_(i.keyed_children)
        data = dict(kct="foo", koct="bar")
        expected = dict(kct="foo", koct="bar")
        res = i._validate(data)
        self.assert_(res == expected, res)

    def testRollupChildValidationErrors(self):
        """
        a validator on a compound widget can propogate error_msgs to
        the children
        """
        expected = dict(c1="foo", c2="bar")

        class V(vd.Validator):
            def _validate_python(self, value, state):
                err = vd.ValidationError("fail")
                err.error_dict = expected
                raise err

        class T(wd.CompoundWidget):
            validator = V()
            children = [wd.Widget(id="c1"),
                        wd.Widget(id="c2")]

        i = T(id="goo").req()
        try:
            i.validate({})
            self.assert_(False)
        except vd.ValidationError as ve:
            for c in ve.widget.children:
                self.assert_(expected[c.id] == c.error_msg, (expected,
                                                                  c.id,
                                                                  c.error_msg))


class TestRepeatingWidget(TestCase):
    def testChildsChildren(self):
        """
        if child and childen defined, children become children of child
        """
        class T(wd.RepeatingWidget):
            child = wd.Widget
            children = [wd.Widget(id="foo")]
        self.assert_(len(T().req().child.children) == 1)

    def testRepeatingWithKeyDifferentFromId(self):
        class T(wd.RepeatingWidget):
            id = 'foo'
            key = 'bar'
            child = wd.Widget

        w = T().req(value=['1', '2', '3'])
        self.assertEquals(w.children[0].compound_key, 'bar:0')

    def testNonWidgetChild(self):
        """
        should throw an error if child is not a widget
        """
        try:
            class T(wd.RepeatingWidget):
                child = ""
            self.assert_(False)
        except pm.ParameterError:
            self.assert_(True)
    def testChildWIdgetWithID(self):
        """
        parameter error raised if child has id
        """
        try:
            class T(wd.RepeatingWidget):
                child = wd.Widget(id="foo")
            self.assert_(False)
        except pm.ParameterError:
            self.assert_(True)

    def testMaxRepitions(self):
        """
        truncate reps based on max_reps??
        """
        class T(wd.RepeatingWidget):
            template = ""
            child = wd.Widget(template="")
            max_reps = 1
            extra_reps = 2

        i = T().req()
        i.prepare()
        self.assert_(i.repetitions == T.max_reps, i.repetitions)

    def testPrepareNoRepitions(self):
        """
        for coverage. call prepare on self.children[0](self.child) when other params aren't specified
        """
        class K(wd.Widget):
            def prepare(self):
                self._prepared = True

        class T(wd.RepeatingWidget):
            child = K()

        i = T().req()
        i.prepare()
        self.assert_(i.children[0]._prepared)


    def testValidator(self):
        class V(vd.Validator):
            def to_python(self, data, state=None):
                self._called = True
        class T(wd.RepeatingWidget):
            child = wd.Widget()
            validator = V()

        i = T().req()
        i.validate({})
        self.assert_(i.validator._called)

class TestDisplayOnlyWidget(TestCase):

    def testInvalidChildError(self):
        class NotAWidget(object):
            pass
        try:
            class T(wd.DisplayOnlyWidget):
                child=NotAWidget()

            self.assert_(False)
        except pm.ParameterError as pe:
            self.assert_("must be" in str(pe))
    def testChildNoID(self):
        try:
            class T(wd.DisplayOnlyWidget):
                id="bar"
                child=wd.Widget(id="foo")

            self.assert_(False)
        except pm.ParameterError as pe:
            self.assert_(" id" in str(pe))


    def testCompoundIDElem(self):
        class Parent(wd.RepeatingWidget):
            child = wd.DisplayOnlyWidget
        self.assert_(Parent(id="goo").req()._compound_id_elem("url"))

    def testChildError(self):
        """
        call validate on child when validated
        """
        err = vd.ValidationError("Failed")

        class V(vd.Validator):
            def to_python(self, value, state=None):
                raise err

        class C(wd.Widget):
            validator = V()

        class T(wd.DisplayOnlyWidget):
            child = C(id="foo")

        try:
            T().req().validate({})
            self.assert_(False)
        except vd.ValidationError as ve:
            self.assert_(ve.widget.child.error_msg == err.message,
                         (ve.widget.child.error_msg))

    def testChildrenDeep(self):
        """
        delegates to it's child for children_deep method
        """
        class C(wd.Widget):
            @classmethod
            def children_deep(cls):
                yield "called"

        class T(wd.DisplayOnlyWidget):
            child = C(id="foo")

        self.assert_(list(T.children_deep())[0] == "called")
