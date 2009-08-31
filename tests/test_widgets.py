import tw2.core as twc, testapi, tw2.core.testbase as tb
import tw2.core.widgets as wd, tw2.core.validation as vd, tw2.core.params as pm
from nose.tools import eq_
from webob import Request
from nose.tools import raises
import formencode as fe

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
            template = 'mako:tw2.core.test_templates.simple_mako'
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
    def validate_python(self, params, state=None):
        raise vd.ValidationError('I always throw up on roller coasters.')
class AlwaysValidateFalseWidget(wd.Widget):
    validator = AlwaysValidateFalseValidator()
    template = "mako:tw2.core.test_templates.always_validate_false_widget"

class CompoundTestWidget(wd.CompoundWidget):
    children = [AlwaysValidateFalseWidget(id="something"),]

class TWidget(wd.Widget):
    template = "tw2.core.test_templates.display_only_test_widget"

class TestWidget(tb.WidgetTest):
    widget = TWidget
    attrs = {'id':"w", 'validator':AlwaysValidateFalseValidator}
    expected = """<p>Test Widget</p>"""
    validate_params = [[None, {'w':''}, None, vd.ValidationError],[None, {}, None, vd.ValidationError]]

    def test_fe_validator(self):
        class FEWidget(wd.Widget):
            validator = fe.validators.Int()
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


class TestSubCompoundWidget(tb.WidgetTest):
    widget = SubCompoundTestWidget
    attrs = {'id':"rw", 'repetitions':1, 'validator':AlwaysValidateFalseValidator}
    expected = """<p>Test Widget</p>"""
    validate_params = [[None, {'rw':''}, None, vd.ValidationError]]

    def test_string_value(self):
        w = self.widget(**self.attrs)()
        w.value = "value"
        r = w.display("value")
        eq_(r.strip(), self.expected)

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
    expected = """<p>Test Widget</p>"""
    validate_params = [[None, {'rw':''}, None, vd.ValidationError], [None, {'rw':'asdf'}, None, vd.ValidationError]]

class RepeatingTestWidget(wd.RepeatingWidget):
    child = AlwaysValidateFalseWidget

class TestRepeatingWidget(tb.WidgetTest):
    widget = RepeatingTestWidget
    attrs = {'id':"rw", 'repetitions':1, 'validator':AlwaysValidateFalseValidator}
    expected = """<p>Test Widget</p>"""
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

class DisplayOnlyTestWidget(wd.DisplayOnlyWidget):
    child = twc.Variable(default=AlwaysValidateFalseWidget)
    template = "tw2.core.test_templates.display_only_test_widget"

class TestDisplayOnlyWidget(tb.WidgetTest):
    widget = DisplayOnlyTestWidget
    attrs = {'id':"dotw"}
    expected = """<p>Test Widget</p>"""
    validate_params = [[None, {'dotw':''}, None, vd.ValidationError]]

    @raises(pm.ParameterError)
    def test_post_init_fail(self):
        class DummyWidget(wd.Widget): pass
        class DummyDOTestWidget(wd.DisplayOnlyWidget):
            template = "tw2.core.test_templates.display_only_test_widget"
            child=DummyWidget(id="lala")
        w = DummyDOTestWidget(id="something")

    @raises(pm.ParameterError)
    def test_childclass_not_widget_fail(self):
        class DummyWidget(wd.Widget): pass
        class DummyDOTestWidget(wd.DisplayOnlyWidget):
            template = "tw2.core.test_templates.display_only_test_widget"
            child="something"
        w = DummyDOTestWidget(id="something")

    def test_class_with_children(self):
        class DummyWidget(wd.Widget): pass
        class DummyDOTestWidget(wd.DisplayOnlyWidget):
            template = "tw2.core.test_templates.display_only_test_widget"
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
        tb.assert_eq_xml(r.body, """<html>
<head><title>some title</title></head>
<body><h1>some title</h1></body>
</html>""")
