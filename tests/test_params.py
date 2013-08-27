from __future__ import print_function
from nose.tools import eq_
import tw2.core as twc, testapi
import six

class Test(six.with_metaclass(twc.params.ParamMeta, object)):
    test1 = twc.Param('test_1', default=10)

class Test2(Test):
    test2 = twc.Param('test_2', default=20)

class TestContainer(twc.CompoundWidget):
    test = twc.ChildParam(default=10)
    test2 = twc.ChildParam()

class Test7(twc.Widget):
    test = twc.Param()


class TestParams(object):
    def setUp(self):
        testapi.setup()

    #---
    # WidgetMeta
    #--
    def test_parameter(self):
        "Check a simple parameter"

        class Test(six.with_metaclass(twc.params.ParamMeta, object)):
            test1 = twc.Param('test_1', default=10)

        assert(len(Test._params) == 1)
        assert(Test._params['test1'].description == 'test_1')
        assert(Test.test1 == 10)

    def test_inherit(self):
        "Check inheritence"
        assert(len(Test2._params) == 2)
        assert(Test2._params['test1'].description == 'test_1')
        assert(Test2._params['test2'].description == 'test_2')
        assert(Test2.test1 == 10)
        assert(Test2.test2 == 20)

    def test_multi_inherit(self):
        "Check multiple inheritence"
        class Test3(Test):
            test3 = twc.Param('test_3')
        class Test4(Test2, Test3):
            pass
        assert(len(Test4._params) == 3)
        assert(sorted(Test4._params.keys()) == ['test1', 'test2', 'test3'])

    def test_override(self):
        "Check overriding a parameter"
        class Test8(Test):
            test1 = twc.Param(request_local=False)
        assert(Test8._params['test1'].default == 10)
        assert(Test._params['test1'].request_local == True)
        assert(Test8._params['test1'].request_local == False)

    def test_override_default(self):
        "Check overriding a parameter default"

        class Test5(Test):
            test1 = 11

        eq_(Test.test1, 10)
        eq_(Test5.test1, 11)

    def test_child(self):
        assert(not hasattr(TestContainer, 'test'))
        test = twc.Widget(id='q')
        assert(not hasattr(test, 'test'))
        test2 = TestContainer(id='r', children=[test]).req()
        assert(test2.c.q.test == 10)

    def test_required(self):
        """ Ensure that twc.Required works.  For issue #25. """

        class TestWidget(twc.Widget):
            template = "whatever"
            inline_engine_name="mako"
            some_param = twc.Param(default=twc.Required)

        try:
            TestWidget.display()
            assert False, "Should have raised an exception."
        except ValueError as e:
            print(str(e))
            assert(str(e).startswith("'some_param' is a required Parameter"))
