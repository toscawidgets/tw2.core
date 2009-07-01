import tw2.core as twc, testapi
try:
    import formencode
except ImportError:
    formencoe = None

compound_widget = twc.CompoundWidget(id='a', children=[
    twc.Widget(id='b', validator=twc.Validator(required=True)),
    twc.Widget(id='c', validator=twc.Validator(required=True)),
])

repeating_widget = twc.RepeatingWidget(id='a', child=
    twc.Widget(validator=twc.Validator(required=True))
)

class TestValidation(object):
    def setUp(self):
        testapi.setup()

    def test_catch_errors(self):
        try:
            twc.validation.catch_errors(lambda s, x: formencode.validators.Int.to_python(x))(None, 'x')
            assert(False)
        except twc.ValidationError:
            pass

    def test_unflatten(self):
        assert(twc.validation.unflatten_params({'a':1, 'b:c':2}) ==
            {'a':1, 'b':{'c':2}})
        assert(twc.validation.unflatten_params({'a:b:c':2}) ==
            {'a': {'b':{'c':2}}})
        assert(twc.validation.unflatten_params({'a:b:c':2, 'a:b:d':3}) ==
            {'a': {'b':{'c':2, 'd':3}}})
        assert(twc.validation.unflatten_params({'a:b:c':2, 'a:b:d':3, 'a:e':4}) ==
            {'a': {'b':{'c':2, 'd':3}, 'e':4}})

        assert(twc.validation.unflatten_params({'a:1':20, 'a:2':10}) ==
            {'a':[20, 10]})
        assert(twc.validation.unflatten_params({'a:1':20, 'b:2':10}) ==
            {'a':[20], 'b':[10]})
        assert(twc.validation.unflatten_params({'a:1':20, 'a:x':10}) ==
            {'a':{'1':20, 'x':10}})

    def test_auto_unflatten(self):
        test = twc.CompoundWidget(id='a', children=[
            twc.Widget(id='b', validator=twc.Validator(required=True)),
        ])
        testapi.request(1)
        assert(test.validate({'a:b':'10'}) == {'b':'10'})

    def test_meta_msgs(self):
        class A(object):
            __metaclass__ = twc.validation.ValidatorMeta
            msgs = {'a':'b'}
        class B(A):
            msgs = {'b':'c'}
        assert(B.msgs == {'a':'b', 'b':'c'})

    def test_prepare_validate(self):
        class MyValidator(twc.Validator):
            def from_python(self, value):
                return value.upper()
        test = twc.Widget(id='a', template='b', validator=MyValidator()).req()
        testapi.request(1)
        test.value = 'fred'
        test.prepare()
        assert(test.value == 'FRED')

    def test_ve_string(self):
        try:
            raise twc.ValidationError('this is a test')
        except twc.ValidationError, e:
            assert(str(e) == 'this is a test')

    def test_ve_rewrite(self):
        try:
            raise twc.ValidationError('required')
        except twc.ValidationError, e:
            assert(str(e) == 'Enter a value')

    def test_ve_subst(self):
        try:
            vld = twc.IntValidator(max=10)
            raise twc.ValidationError('toobig', vld)
        except twc.ValidationError, e:
            assert(str(e) == 'Cannot be more than 10')

    def test_vld_leaf_pass(self):
        test = twc.Widget(validator=twc.IntValidator())
        assert(test.req()._validate('1') == 1)

    def test_vld_leaf_fail(self):
        test = twc.Widget(validator=twc.IntValidator()).req()
        try:
            test._validate('x')
            assert(False)
        except twc.ValidationError:
            pass

        assert(test.value == 'x')
        assert(test.error_msg == 'Must be an integer')

    def test_compound_pass(self):
        testapi.request(1)
        inp = {'a': {'b':'test', 'c':'test2'}}
        out = compound_widget.validate(inp)
        assert(out == inp['a'])
        cw = twc.core.request_local()['validated_widget']
        assert(cw.children.b.value == 'test')
        assert(cw.children.c.value == 'test2')

    def test_compound_corrupt(self):
        testapi.request(1)
        try:
            compound_widget.validate({'a':[]})
            assert(False)
        except twc.ValidationError:
            pass

    def test_compound_child_fail(self):
        testapi.request(1)
        try:
            compound_widget.validate({'a': {'b':'test'}})
            assert(False)
        except twc.ValidationError:
            pass
        cw = twc.core.request_local()['validated_widget']
        assert(cw.children.b.value == 'test')
        assert('Enter a value' == cw.children.c.error_msg)

    def test_compound_whole_validator(self):
        pass # TBD

    def test_rw_pass(self):
        testapi.request(1)
        rep = repeating_widget.req()
        inp = ['test', 'test2']
        out = rep._validate(inp)
        assert(inp == out)
        assert(rep.children[0].value == 'test')
        assert(rep.children[1].value == 'test2')

    def test_rw_corrupt(self):
        testapi.request(1)
        try:
            repeating_widget.validate({'a':{'a':'b'}})
            assert(False)
        except twc.ValidationError:
            pass

    def test_rw_child_fail(self):
        testapi.request(1)
        try:
            repeating_widget.validate({'a':['test', '']})
            assert(False)
        except twc.ValidationError, e:
            pass
        rw = twc.core.request_local()['validated_widget']
        assert(rw.children[0].value == 'test')
        assert('Enter a value' == rw.children[1].error_msg)

    def test_dow(self):
        test = twc.DisplayOnlyWidget(child=compound_widget)
        testapi.request(1)
        inp = {'a': {'b':'test', 'c':'test2'}}
        out = test.validate(inp)
        assert(out == inp['a'])
        test = twc.core.request_local()['validated_widget']
        assert(test.child.children.b.value == 'test')
        assert(test.child.children.c.value == 'test2')

    #--
    # Test round trip
    #--
    def test_round_trip(self):
        test = twc.CompoundWidget(id='a', children=[
            twc.DisplayOnlyWidget(child=
                twc.RepeatingWidget(id='q', child=twc.Widget)
            ),
            twc.CompoundWidget(id='cc', children=[
                twc.Widget(id='d'),
                twc.Widget(id='e'),
            ])
        ])

        widgets = [
            test.children[0].child.rwbc[0],
            test.children[0].child.rwbc[1],
            test.children.cc.children.d,
            test.children.cc.children.e,
        ]

        data = dict((w.compound_id, 'test%d' % i) for i,w in enumerate(widgets))
        testapi.request(1)
        vdata = test.validate(data)

        test = twc.core.request_local()['validated_widget']
        widgets = [
            test.children[0].child.children[0],
            test.children[0].child.children[1],
            test.children.cc.children.d,
            test.children.cc.children.e,
        ]

        for i,w in enumerate(widgets):
            assert(w.value == 'test%d' % i)
