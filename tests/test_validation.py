import tw2.core as twc, testapi
import tw2.core.testbase as tb
from tw2.core.validation import *
import re
import datetime

from nose.tools import (
    eq_, raises, assert_raises, assert_equals, assert_is_instance)

from types import UnicodeType
from mock import Mock
from webob.multidict import MultiDict
from unittest import TestCase
import sys

try:
    import formencode
    # This is required to make tests pass on non english systems
    formencode.api.set_stdtranslation(languages=['en'])
except ImportError:
    formencode = None

compound_widget = twc.CompoundWidget(id='a', children=[
    twc.Widget(id='b', validator=twc.Validator(required=True)),
    twc.Widget(id='c', validator=twc.Validator(required=True)),
])

repeating_widget = twc.RepeatingWidget(id='a', child=
    twc.Widget(validator=twc.Validator(required=True))
)


class TestValidationError(tb.WidgetTest):
    def test_validator_msg(self):
        twc.core.request_local = tb.request_local_tst
        self.mw.config.validator_msgs['f1'] = 's1'
        self.request(1, self.mw)
        e = ValidationError('f1')
        eq_(e.message,'s1')


def assert_equal_unicode(first, second, msg=None):
    assert_equals(first, second, msg)
    assert_is_instance(first, UnicodeType, msg)
    assert_is_instance(second, UnicodeType, msg)


class TestValidationErrorMessages(object):
    def test_uses_message_as_string_representation(self):
        message = 'Validation message key'

        validation_error = ValidationError(message)

        assert_equals(str(validation_error), message)

    def test_uses_message_as_unicode_representation(self):
        ascii_message = 'Validation message key'

        validation_error = ValidationError(ascii_message)

        assert_equal_unicode(validation_error.__str__(), unicode(ascii_message))


def _test_stupid_fe_import_requirement():
    "i tried, but seriously, sometimes 100% coverage aint worth it"
    import sys
    removed_items = []
    pre = sys.path[:]
    pre_mod = copy.copy(sys.modules)
    del sys.modules['formencode']
    del sys.modules['tw2']
    for item in pre:
        if 'formencode' in item.lower():
            sys.path.remove(item)
            removed_items = item
    import tw2.core.validation
    sys.path = pre
    sys.modules = pre_mod

def test_safe_validate():
    v = Validator(required="true")
    r = safe_validate(v, "asdf")
    eq_(r, "asdf")

def test_safe_validate_invalid():
    v = twc.IntValidator()
    r = safe_validate(v, 'x')
    assert(r is twc.Invalid)

def test_unflatten_params_multi_dict():
    params = unflatten_params(MultiDict((('asdf:f1', 's1'), ('asdf:f2', 's2'))))
    eq_(params, {'asdf': {'f1': 's1', 'f2': 's2'}})


def raise_formencode_validation_error(message):
    raise formencode.Invalid('Some FormEncode validation error', None, None)


class TestCatchErrorsDecorator(object):

    def test_wrapps_and_bubles_up_tw2_validation_errors(self):
        def raise_tw2_validation_error(message):
            raise ValidationError(msg='ToscaWidgets2 validation error')

        with assert_raises(ValidationError):
            catch_errors(raise_tw2_validation_error)(None)

    def test_wrapps_and_bubles_up_formencode_validation_errors(self):
        with assert_raises(ValidationError):
            catch_errors(raise_formencode_validation_error)(None)

    def test_encodes_message_in_unicode(self):
        with assert_raises(ValidationError) as cm:
            catch_errors(raise_formencode_validation_error)(None)

        validation_error = cm.exception

        assert_equal_unicode(validation_error.message, unicode('Some FormEncode validation error'))

    def test_sets_widgets_error_message(self):
        widget = Mock()

        with assert_raises(ValidationError):
            catch_errors(raise_formencode_validation_error)(widget)

        assert_equals(widget.error_msg, u'Some FormEncode validation error')


class TestValidation(TestCase):
    def setUp(self):
        testapi.setup()

    def formencode_skip(self):
        if not formencode:
            if sys.version_info[0] == 2 and sys.version_info[1] == 7:
                self.skipTest("No formencode.")
            else:
                return True  # Just pretend like we passed.

        return False

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

    def test_compound_validation(self):
        """ Tests that compound widgets can do validation

        Not just leaf widgets anymore.

        """
        class NeverValid(Validator):
            msgs = {"never": "this is never valid"}
            def to_python(self, value, state=None):
                raise ValidationError("never", self)

        class FailWidget(twc.CompoundWidget):
            b = twc.Widget
            validator = NeverValid

        try:
            FailWidget.validate({'b':'whatever'})
            assert(False)
        except ValidationError, ve:
            assert(ve.widget.error_msg == NeverValid.msgs['never'])

    def test_compound_validation_formencode(self):
        " Test that compound widgets validate with formencode. """

        if self.formencode_skip():
            return

        class MatchyWidget(twc.CompoundWidget):
            validator = formencode.validators.FieldsMatch('one', 'two')
            one = twc.Widget
            two = twc.Widget

        try:
            MatchyWidget.validate({'one': 'foo', 'two': 'foo'})
        except ValidationError, ve:
            assert False, "Widget should have validated correctly."

        try:
            MatchyWidget.validate({'one': 'foo', 'two': 'bar'})
            assert False, "Widget should not have validated."
        except ValidationError, ve:
            pass

    def test_compound_validation_error_msgs(self):
        " Test that compound widgets error_msgs show up in the right place. "

        if self.formencode_skip():
            return

        class MatchyWidget(twc.CompoundWidget):
            validator = formencode.validators.FieldsMatch('one', 'two')
            one = twc.Widget
            two = twc.Widget
            three = twc.Widget(validator=twc.Validator(required=True))

        try:
            MatchyWidget.validate({'one': 'foo', 'two': 'bar'})
            assert False, "Widget should not have validated."
        except ValidationError, ve:
            assert 'do not match' in ve.widget.children[0].error_msg
            assert 'do not match' not in ve.widget.error_msg
            assert 'childerror' not in ve.widget.error_msg

        try:
            MatchyWidget.validate({'one': 'foo', 'two': 'foo', 'three':''})
            assert False, "Widget should not have validated."
        except ValidationError, ve:
            assert 'Enter a value' in ve.widget.children[2].error_msg
            assert 'Enter a value' not in ve.widget.error_msg
            assert 'childerror' not in ve.widget.error_msg

    def test_auto_unflatten(self):
        test = twc.CompoundWidget(id='a', children=[
            twc.Widget(id='b', validator=twc.Validator(required=True)),
        ])
        testapi.request(1)
        eq_(test.validate({'a:b':'10'}), {'b':'10'})

    def test_unflatten_decode(self):
        assert(twc.validation.unflatten_params({'a': u'\u1234'.encode('utf-8')}) == {'a':u'\u1234'})

    def test_unflatten_error(self):
        try:
            twc.validation.unflatten_params({'a': chr(128)})
            assert(False)
        except twc.ValidationError, e:
            eq_(str(e), "Received in wrong character set; should be utf-8")

    def test_meta_msgs(self):
        class A(object):
            __metaclass__ = twc.validation.ValidatorMeta
            msgs = {'a':'b'}
        class B(A):
            msgs = {'b':'c'}
        assert(B.msgs == {'a':'b', 'b':'c'})

    def test_prepare_validate(self):
        class MyValidator(twc.Validator):
            def from_python(self, value, state=None):
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

        eq_(test.value, 'x')
        eq_(test.error_msg, 'Must be an integer')

    def test_compound_pass(self):
        testapi.request(1)
        inp = {'a': {'b':'test', 'c':'test2'}}
        out = compound_widget.validate(inp)
        eq_(out, inp['a'])
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

    def test_compound_keyed_children(self):
        if self.formencode_skip():
            return

        compound_keyed_widget = twc.CompoundWidget(id='a', children=[
            twc.Widget(id='b', key='x', validator=twc.Validator(required=True)),
            twc.Widget(id='c', key='y', validator=formencode.validators.OpenId()),
        ])

        testapi.request(1)
        inp = {'a': {'x':'test', 'y':'test2'}}
        try:
            compound_keyed_widget.validate(inp)
            assert False
        except twc.ValidationError, e:
            pass

        cw = twc.core.request_local()['validated_widget']
        assert "is not a valid OpenId" in cw.children.c.error_msg

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

    def test_display_only_widget(self):
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
            eq_(w.value, 'test%d' % i)

class TestValidator(tb.ValidatorTest):
    validator = Validator
    attrs =    [{}, {'required':True}]
    params =   ['', '']
    expected = [None, ValidationError]

    from_python_attrs =    [{}, {'required':True}]
    from_python_params =   ['', 'asdf']
    from_python_expected = ['', 'asdf']

    def test_clone(self):
        v = Validator()
        assert v.required == False
        v2 = v.clone(required=True)
        assert v2.required == True

    def test_repr_(self):
        v = Validator()
        r = repr(v)
        eq_(r, "Validator(required=False, strip=True)")

class TestLengthValidator(tb.ValidatorTest):
    validator = LengthValidator
    attrs =    [{}, {}, {'max':3}, {'max':3}, {'max':3}, {'min':3}, {'min':3}, {'min':3}]
    params =   ['', 'asdf', 'as', 'asd', 'asdf', 'as', 'asd', 'asdf']
    expected = [None, None, None, None, ValidationError, ValidationError, None, None]

class TestIntValidator(tb.ValidatorTest):
    validator = IntValidator
    to_python_attrs =    [{}, {}, {}, {}]
    to_python_params =   [1, '1', '1.5', '']
    to_python_expected = [1, 1, ValidationError, None]

    from_python_attrs =    [{}, {}, {}]
    from_python_params =   [1, '1', '1.5']
    from_python_expected = ['1', '1', ValidationError]

    attrs =    [{}, {}, {}, {}, {'max':12}, {'max':12},{'min':12}, {'min':12}, ]
    params =   [1,    '1', '1.5',           'asdf', '11', '13', '11', '13']
    expected = [None, None, ValidationError, ValidationError, None, ValidationError, ValidationError, None]

    @raises(ValidationError)
    def test_required(self):
        v = IntValidator(required=True)
        v.validate_python(v.to_python(''))


class TestBoolValidator(tb.ValidatorTest):
    validator = BoolValidator
    to_python_attrs =    [{}, {}, {}, {}, {}, {}, {}, {}, {},]
    to_python_params =   ['on', 'yes', 'true', '1', 1, True, 'Yes', 'True', 'off']
    to_python_expected = [True, True, True, True, True, True, True, True, False]

class TestOneOfValidator(tb.ValidatorTest):
    validator = OneOfValidator
    attrs =    [{'values':['a', 'b', 'c']}, {'values':['a', 'b', 'c']}]
    params =   ['a', 'd']
    expected = [None, ValidationError]

class TestDateValidator(tb.ValidatorTest):
    validator = DateValidator
    to_python_attrs =    [{}, {}]
    to_python_params =   ['01/01/2009', 'asdf']
    to_python_expected = [datetime.date(2009, 1, 1), ValidationError]

    attrs = [{'required': False}, {'required': True}]
    params = ['', '']
    expected = [None, ValidationError]

    from_python_attrs = [{}, {}]
    from_python_params = [datetime.date(2009, 1, 1)]
    from_python_expected = ['01/01/2009']

    def test_max_str(self):
        expected = '31/12/2009'
        r = DateValidator(max=datetime.date(2009, 12, 31)).max_str
        eq_(r, expected)

    def test_min_str(self):
        expected = '31/12/2009'
        r = DateValidator(min=datetime.date(2009, 12, 31)).min_str
        eq_(r, expected)

class TestDatetimeValidator(tb.ValidatorTest):
    validator = DateTimeValidator
    to_python_attrs =    [{}, {}]
    to_python_params =   ['01/01/2009 01:00', 'asdf']
    to_python_expected = [datetime.datetime.strptime('1/1/2009 1:00', '%d/%m/%Y %H:%M'), ValidationError]

    attrs = [{'required': False}, {'required': True}]
    params = ['', '']
    expected = [None, ValidationError]

    from_python_attrs = [{}, {}]
    from_python_params = [datetime.datetime.strptime('1/1/2009 1:00', '%d/%m/%Y %H:%M')]
    from_python_expected = ['01/01/2009 01:00']

class TestRegexValidator(tb.ValidatorTest):
    validator = RegexValidator
    attrs =    [{'regex':re.compile("asdf")}, {'regex':re.compile("qwer")}]
    params =   ['asdf', 'asdf']
    expected = [None, ValidationError]

class TestEmailValidator(tb.ValidatorTest):
    validator = EmailValidator
    attrs =    [{}, {}]
    params =   ['someone@somewhere.com', 'asdf']
    expected = [None, ValidationError]

class TestUrlValidator(tb.ValidatorTest):
    validator = UrlValidator
    attrs =    [{}, {}]
    params =   ['http://www.google.com', 'asdf']
    expected = [None, ValidationError]

class TestIPAddressValidator(tb.ValidatorTest):
    validator = IpAddressValidator
    attrs =    [{}, {}]
    params =   ['123.123.123.123', 'asdf']
    expected = [None, ValidationError]


class TestValidatorMisc(TestCase):
    def testRequired(self):
        v = Validator(required=True)
        self.assert_(v.required)
        try:
            v.validate_python(None)
            assert False
        except ValidationError, ve:
            self.assert_(ve.message == v.msgs["required"], ve.message)

    def testBlankValidator(self):
        v = BlankValidator()
        self.assert_(v.to_python(None) == EmptyField)

    def testRangeValidator(self):
        v = RangeValidator(min=0, max=2)
        self.assert_(v.min is not None)
        self.assert_(v.max is not None)
        try:
            v.validate_python(v.min - 1)
            assert False
        except ValidationError, ve:
            self.assert_(ve.message.startswith(v.msgs["toosmall"][:5]),
                         (ve.message, v.msgs))

        try:
            v.validate_python(v.max + 1)
            assert False
        except ValidationError, ve:
            self.assert_(ve.message.startswith(v.msgs["toobig"][:5]),
                         (ve.message, v.msgs))

        v.validate_python(v.min)
        v.validate_python(v.max)

    def testIPAddressValidator(self):
        ip_block = "192.168.0.0/24"
        bad_ip_block = "192.168.0.0/64"
        ip = "192.168.1.1"
        v = IpAddressValidator(allow_netblock=False)

        try:
            v.validate_python(ip_block)
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(ve.message.startswith(v.msgs["badipaddress"][:5]))

        v.allow_netblock = True

        try:
            v.validate_python(bad_ip_block)
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(ve.message.startswith(v.msgs["badnetblock"][:5]))

        v.require_netblock = True

        try:
            v.validate_python(ip)
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(ve.message.startswith(v.msgs["badnetblock"][:5]))

    def testMatchValidator(self):
        v = MatchValidator(other_field="foo")

        try:
            v.validate_python("bar", {v.other_field: "foo"})
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(ve.message.startswith(v.msgs["mismatch"][:5]))

    def testInValidatorRequired(self):
        v = IntValidator(required=True)
        self.assert_(v.required)
        try:
            v.validate_python(None)
            self.assert_(False)
        except ValidationError, ve:
            self.assert_("Enter a value" in ve.message, ve.message)

    def testAnyValidator(self):
        v = Any(
            twc.StringLengthValidator(min=5, max=6),
            twc.IpAddressValidator,
            required=True
        )

        self.assert_(v.required)
        try:
            v.validate_python("20")
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(
                ("valid IP" in ve.message and "at least 5" in ve.message),
                ve.message
            )

        try:
            v.validate_python("xxxxxxxxxx")
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(
                ("valid IP" in ve.message and "longer than 6" in ve.message),
                ve.message
            )

        try:
            v.validate_python("xxxxx")
            self.assert_(True)
        except ValidationError, ve:
            self.assert_(False)

        try:
            v.validate_python("127.0.0.1")
            self.assert_(True)
        except ValidationError, ve:
            self.assert_(False)

    def testAllValidator(self):
        v = All(
            twc.StringLengthValidator(min=9, max=9),
            twc.IpAddressValidator,
            required=True
        )

        self.assert_(v.required)
        try:
            v.validate_python("127.0.0.10")
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(
                ("longer than 9" in ve.message),
                ve.message
            )

        try:
            v.validate_python("0.0.0.0")
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(
                ("valid IP" not in ve.message and "9" in ve.message),
                ve.message
            )

        try:
            v.validate_python("12345678")
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(
                ("valid IP" in ve.message and "9" in ve.message),
                ve.message
            )

        try:
            v.validate_python("123456789")
            self.assert_(False)
        except ValidationError, ve:
            self.assert_(
                ("valid IP" in ve.message and "9" not in ve.message),
                ve.message
            )

        try:
            v.validate_python("127.0.0.1")
            self.assert_(True)
        except ValidationError, ve:
            self.assert_(False, ve.message)
