from nose.tools import eq_
import tw2.core as twc, testapi

class TestHierarchy(object):
    def setUp(self):
        testapi.setup()

    #--
    # Compound IDs
    #--
    def test_compound_id(self):
        test = twc.CompoundWidget(id='x', children=[
            twc.Widget(id='a'),
            twc.Widget(id='b'),
        ])
        assert(test.children.a.compound_id == 'x:a')

    def test_invalid_id(self):
        try:
            a = twc.Widget(id=':')
            assert(False)
        except twc.ParameterError as e:
            eq_(str(e), "Not a valid W3C id: ':'")

    def test_id_none(self):
        test = twc.Widget(id=None)
        assert(test.compound_id == None)

    def test_repeating_id(self):
        test = twc.RepeatingWidget(id='x', child=twc.Widget)
        assert(test.rwbc[3].compound_id == 'x:3')

    #--
    # CompoundWidget / WidgetBunch
    #--
    def test_widgetbunch(self):
        a = twc.Widget(id='a')
        b = twc.Widget(id='b')
        test = twc.widgets.WidgetBunch([a, b])
        assert(len(test) == 2)
        assert([w for w in test] == [a, b])
        assert(test[0] is a)
        assert(test[1] is b)
        assert(test.a is a)
        assert(test.b is b)
        try:
            test.c
            assert(False)
        except AttributeError as e:
            assert(str(e) == "Widget has no child named 'c'")

    def xxtest_wb_nonwidget(self):
        try:
            test = twc.widgets.WidgetBunch(['hello'])
            assert(False)
        except twc.WidgetError as e:
            assert(str(e) == 'WidgetBunch may only contain Widgets')

    def xxtest_wb_dupe(self):
        try:
            test = twc.widgets.WidgetBunch([twc.Widget(id='a'), twc.Widget(id='a')])
            assert(False)
        except twc.WidgetError as e:
            assert(str(e) == "WidgetBunch contains a duplicate id 'a'")

    def test_cw_propagate(self):
        testb = twc.CompoundWidget(id='a', template='x', children=[
            twc.Widget(id='b'),
            twc.Widget(id='c'),
        ])
        test = testb.req(value = {'b':1, 'c':2})
        test.prepare()
        assert(test.children.b.value == 1)
        assert(test.children.c.value == 2)

        class A:
            pass
        a = A()
        a.b = 10
        a.c= 20
        test = testb.req(value = a)
        test.prepare()
        assert(test.children.b.value == 10)
        assert(test.children.c.value == 20)


    #--
    # Repeating Widget Bunch
    #--
    def test_rwb(self):
        test = twc.RepeatingWidget(child=twc.Widget).req()
        testapi.request(1)
        test.value = ['a', 'b', 'c']
        test.prepare()
        for i in range(4):
            assert(test.children[i].repetition == i)
        assert(test.children[0] is not test.children[1])

    def test_rw_propagate(self):
        test = twc.RepeatingWidget(child=twc.Widget).req()
        testapi.request(1)
        test.value = ['a', 'b', 'c']
        test.prepare()
        assert(len(test.children) == 3)
        assert([w.value for w in test.children] == ['a', 'b', 'c'])

    def test_rw_length(self):
        testb = twc.RepeatingWidget(child=twc.Widget)

        test = testb.req(value=list(range(10)))
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 10)

        test = testb.req(value=list(range(10)))
        test.extra_reps = 5
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 15)

        test = testb.req(value=list(range(10)))
        test.max_reps = 10
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 10)

        test = testb.req(value=list(range(10)))
        test.max_reps = 30
        test.min_reps = 20
        test.repetitions = None
        test.prepare()
        assert(test.repetitions == 20)

    #--
    # Display only
    #--
    def test_display_only(self):
        a = twc.Widget(id='a')
        test = twc.DisplayOnlyWidget(child=a, template='xyz')
        assert(a.parent is None)
        assert(test.child.parent.template == test.template)
        testapi.request(1)
        test = test.req()
        test.value = 10
        test.prepare()
        assert(test.child.value == 10)

    #
    # Display Only with inheritance
    def test_display_only_inherit(self):
        class a(twc.DisplayOnlyWidget):
            child = twc.CompoundWidget
            wdgt = twc.Widget()

        class b(a):
            wdgt2 = twc.Widget()
        
        test = b()
        assert 'wdgt' in [c.id for c in test.child.children]
        assert 'wdgt2' in [c.id for c in test.child.children]

