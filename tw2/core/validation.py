from . import core
import re
from . import util
import string
import datetime
import copy
import functools
import webob
import warnings
import uuid

from .i18n import _
import six

# Compat
if six.PY3:
    capitalize = str.capitalize
else:
    capitalize = string.capitalize

# This hack helps work with different versions of WebOb
if not hasattr(webob, 'MultiDict'):
    # Check for webob versions with UnicodeMultiDict
    if hasattr(webob.multidict, 'UnicodeMultiDict'):
        webob.MultiDict = webob.multidict.UnicodeMultiDict
    else:
        webob.MultiDict = webob.multidict.MultiDict

try:
    import formencode
except ImportError:
    formencode = None


class Invalid(object):
    pass


class EmptyField(object):
    pass


if formencode:
    class BaseValidationError(core.WidgetError, formencode.Invalid):
        def __init__(self, msg):
            formencode.Invalid.__init__(self, msg, None, None)
else:
    class BaseValidationError(core.WidgetError):
        def __init__(self, msg):
            core.WidgetError.__init__(self, msg)
            self.msg = msg


class ValidationError(BaseValidationError):
    """Invalid data was encountered during validation.

    The constructor can be passed a short message name, which is looked up in
    a validator's :attr:`msgs` dictionary. Any values in this, like
    ``$val``` are substituted with that attribute from the validator. An
    explicit validator instance can be passed to the constructor, or this
    defaults to :class:`Validator` otherwise.
    """
    def __init__(self, msg, validator=None, widget=None):
        self.widget = widget
        validator = validator or Validator
        mw = core.request_local().get('middleware')
        if isinstance(validator, Validator):
            msg = validator.msg_rewrites.get(msg, msg)

        if mw and msg in mw.config.validator_msgs:
            msg = mw.config.validator_msgs[msg]
        elif hasattr(validator, 'msgs') and msg in validator.msgs:
            msg = validator.msgs.get(msg, msg)

        # In the event that the user specified a form-wide validator but
        # they did not specify a childerror message, show no error.
        if msg == 'childerror':
            msg = ''

        msg = re.sub('\$(\w+)',
                lambda m: str(getattr(validator, m.group(1))), six.text_type(msg))
        super(ValidationError, self).__init__(msg)

    @property
    def message(self):
        """Added for backwards compatibility.  Synonymous with `msg`."""
        return self.msg


catch = ValidationError
if formencode:
    catch = (catch, formencode.Invalid)


def safe_validate(validator, value, state=None):
    try:
        return validator.to_python(value, state=state)
    except catch:
        return Invalid


def catch_errors(fn):
    @functools.wraps(fn)
    def wrapper(self, *args, **kw):
        try:
            d = fn(self, *args, **kw)
            return d
        except catch as e:
            e_msg = six.text_type(e)
            if self:
                self.error_msg = e_msg
            raise ValidationError(e_msg, widget=self)
    return wrapper


def unflatten_params(params):
    """This performs the first stage of validation. It takes a dictionary where
    some keys will be compound names, such as "form:subform:field" and converts
    this into a nested dict/list structure. It also performs unicode decoding,
    with the encoding specified in the middleware config.
    """
    if isinstance(params, webob.MultiDict):
        params = params.mixed()

    mw = core.request_local().get('middleware')
    enc = mw.config.encoding if mw else 'utf-8'

    try:
        for p in params:
            if isinstance(params[p], six.binary_type):
                params[p] = params[p].decode(enc)
    except UnicodeDecodeError:
        raise ValidationError('decode', Validator(encoding=enc))

    out = {}
    for pname in params:
        dct = out
        elements = pname.split(':')
        for e in elements[:-1]:
            dct = dct.setdefault(e, {})
        dct[elements[-1]] = params[pname]

    numdict_to_list(out)
    return out

number_re = re.compile('^\d+$')


def numdict_to_list(dct):
    for k, v in dct.items():
        if isinstance(v, dict):
            numdict_to_list(v)
            if all(number_re.match(k) for k in v):
                dct[k] = [v[x] for x in sorted(v, key=int)]


class ValidatorMeta(type):
    """Metaclass for :class:`Validator`.

    This makes the :attr:`msgs` dict copy from its base class.
    """
    def __new__(meta, name, bases, dct):
        if 'msgs' in dct:
            msgs = {}
            rewrites = {}
            for b in bases:
                try:
                    msgs.update(b.msgs)
                    rewrites.update(b.msgs_rewrites)
                except AttributeError:
                    pass
            msgs.update(dct['msgs'])
            add_to_msgs = {}
            del_from_msgs = []
            for m, d in msgs.items():
                if isinstance(d, tuple):
                    add_to_msgs[d[0]] = d[1]
                    rewrites[m] = d[0]
                    del_from_msgs.append(m)
            msgs.update(add_to_msgs)
            for m in del_from_msgs:
                del msgs[m]
            dct['msgs'] = msgs
            dct['msg_rewrites'] = rewrites
        if 'validate_python' in dct and '_validate_python' not in dct:
            dct['_validate_python'] = dct.pop('validate_python')
            warnings.warn('validate_python() is deprecated;'
                ' use _validate_python() instead',
                DeprecationWarning, stacklevel=2)
        return type.__new__(meta, name, bases, dct)


class Validator(six.with_metaclass(ValidatorMeta, object)):
    """Base class for validators

    `required`
        Whether empty values are forbidden in this field. (default: False)

    `strip`
        Whether to strip leading and trailing space from the input, before
        any other validation. (default: True)

    To convert and validate a value to Python, use the :meth:`to_python`
    method, to convert back from Python, use :meth:`from_python`.

    To create your own validators, sublass this class, and override any of
    :meth:`_validate_python`, :meth:`_convert_to_python`,
    or :meth:`_convert_from_python`. Note that these methods are not
    meant to be used externally. All of them may raise ValidationErrors.

    """

    msgs = {
        'required': _('Enter a value'),
        'decode': _('Received in wrong character set; should be $encoding'),
        'corrupt': _('Form submission received corrupted; please try again'),
        'childerror': '',  # Children of this widget have errors
    }
    required = False
    strip = True
    if_empty = None

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])

    def to_python(self, value, state=None):
        """Convert an external value to Python and validate it."""
        if self._is_empty(value):
            if self.required:
                raise ValidationError('required', self)
            return self.if_empty
        if self.strip and isinstance(value, six.string_types):
            value = value.strip()
        value = self._convert_to_python(value, state)
        self._validate_python(value, state)
        return value

    def from_python(self, value, state=None):
        """Convert from a Python object to an external value."""
        if self._is_empty(value):
            return ''
        if isinstance(value, six.string_types) and self.strip:
            value = value.strip()
        value = self._convert_from_python(value, state)
        return value

    def __repr__(self):
        _bool = ['False', 'True']
        return ("Validator(required=%s, strip=%s)" %
            (_bool[int(self.required)], _bool[int(self.strip)]))

    def _validate_python(self, value, state=None):
        """"Overridable internal method for validation of Python values."""
        pass

    def _convert_to_python(self, value, state=None):
        """"Overridable internal method for conversion to Python values."""
        return value

    def _convert_from_python(self, value, state=None):
        """"Overridable internal method for conversion from Python values."""
        return value

    @staticmethod
    def _is_empty(value):
        """Check whether the given value should be considered "empty"."""
        return value is None or value == '' or (
            isinstance(value, (list, tuple, dict)) and not value)

    def validate_python(self, value, state=None):
        """"Deprecated, use :meth:`_validate_python` instead.

        This method has been renamed in FormEncode 1.3 and ToscaWidgets 2.2
        in order to clarify that is an internal method that is meant to be
        overridden only; you must call meth:`to_python` to validate values.

        """
        warnings.warn('validate_python() is deprecated;'
            ' use _validate_python() instead',
            DeprecationWarning, stacklevel=2)
        return self._validate_python(value, state)

    def clone(self, **kw):
        nself = copy.copy(self)
        for k in kw:
            setattr(nself, k, kw[k])
        return nself

if formencode:
    validator_classes = (Validator, formencode.Validator)
else:
    validator_classes = (Validator, )


class BlankValidator(Validator):
    """
    Always returns EmptyField. This is the default for hidden fields,
    so their values are not included in validated data.
    """
    def to_python(self, value, state=None):
        return EmptyField


class LengthValidator(Validator):
    """
    Confirm a value is of a suitable length. Usually you'll use
    :class:`StringLengthValidator` or :class:`ListLengthValidator` instead.

    `min`
        Minimum length (default: None)

    `max`
        Maximum length (default: None)
    """
    msgs = {
        'tooshort': _('Value is too short'),
        'toolong': _('Value is too long'),
    }
    min = None
    max = None

    def __init__(self, **kw):
        super(LengthValidator, self).__init__(**kw)
        if self.min:
            self.required = True

    def _validate_python(self, value, state=None):
        if self.min and len(value) < self.min:
            raise ValidationError('tooshort', self)
        if self.max and len(value) > self.max:
            raise ValidationError('toolong', self)


class StringLengthValidator(LengthValidator):
    """
    Check a string is a suitable length. The only difference to LengthValidator
    is that the messages are worded differently.
    """

    msgs = {
        'tooshort': (
            'string_tooshort', _('Must be at least $min characters')),
        'toolong': (
            'string_toolong', _('Cannot be longer than $max characters')),
    }


class ListLengthValidator(LengthValidator):
    """
    Check a list is a suitable length. The only difference to LengthValidator
    is that the messages are worded differently.
    """

    msgs = {
        'tooshort': ('list_tooshort', _('Select at least $min')),
        'toolong': ('list_toolong', _('Select no more than $max')),
    }


class RangeValidator(Validator):
    """
    Confirm a value is within an appropriate range. This is not usually used
    directly, but other validators are derived from this.

    `min`
        Minimum value (default: None)

    `max`
        Maximum value (default: None)
    """
    msgs = {
        'toosmall': _('Must be at least $min'),
        'toobig': _('Cannot be more than $max'),
    }
    min = None
    max = None

    def _validate_python(self, value, state=None):
        if self.min is not None and value < self.min:
            raise ValidationError('toosmall', self)
        if self.max is not None and value > self.max:
            raise ValidationError('toobig', self)


class IntValidator(RangeValidator):
    """
    Confirm the value is an integer. This is derived from
    :class:`RangeValidator` so `min` and `max` can be specified.
    """
    msgs = {
        'notint': _('Must be an integer'),
    }

    def _convert_to_python(self, value, state=None):
        try:
            return int(value)
        except ValueError:
            raise ValidationError('notint', self)

    def _convert_from_python(self, value, state=None):
        return str(value)


class BoolValidator(RangeValidator):
    """
    Convert a value to a boolean. This is particularly intended to handle
    check boxes.
    """
    msgs = {
        'required': ('bool_required', _('You must select this'))
    }
    if_empty = False

    def _convert_to_python(self, value, state=None):
        return str(value).lower() in ('on', 'yes', 'true', '1', 'y', 't')

    def _convert_from_python(self, value, state=None):
        return value and 'true' or 'false'


class OneOfValidator(Validator):
    """
    Confirm the value is one of a list of acceptable values. This is useful for
    confirming that select fields have not been tampered with by a user.

    `values`
        Acceptable values
    """
    msgs = {
        'notinlist': _('Invalid value'),
    }
    values = []

    def _validate_python(self, value, state=None):
        if value not in self.values:
            raise ValidationError('notinlist', self)


class DateTimeValidator(RangeValidator):
    """
    Confirm the value is a valid date and time. This is derived from
    :class:`RangeValidator` so `min` and `max` can be specified.

    `format`
        The expected date/time format. The format must be specified using
        the same syntax as the Python strftime function.
    """
    msgs = {
        'baddatetime': _('Must follow date/time format $format_str'),
        'toosmall': ('date_toosmall', _('Cannot be earlier than $min_str')),
        'toobig': ('date_toobig', _('Cannot be later than $max_str')),
    }
    format = '%Y-%m-%d %H:%M'

    format_tbl = {
        'd': 'day',
        'H': 'hour',
        'I': 'hour',
        'm': 'month',
        'M': 'minute',
        'S': 'second',
        'y': 'year',
        'Y': 'year',
    }

    @property
    def format_str(self):
        f = lambda m: self.format_tbl.get(m.group(1), '')
        return re.sub('%(.)', f, self.format)

    @property
    def min_str(self):
        return self.min.strftime(self.format)

    @property
    def max_str(self):
        return self.max.strftime(self.format)

    def _convert_to_python(self, value, state=None):
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        try:
            return datetime.datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError('baddatetime', self)

    def _validate_python(self, value, state=None):
        super(DateTimeValidator, self)._validate_python(value, state)

    def _convert_from_python(self, value, state=None):
        return value.strftime(self.format)


class DateValidator(DateTimeValidator):
    """
    Confirm the value is a valid date.

    Just like :class:`DateTimeValidator`, but without the time component.
    """
    msgs = {
        'baddatetime': (
            'baddate', _('Must follow date format $format_str')),
    }
    format = '%Y-%m-%d'

    def _convert_to_python(self, value, state=None):
        value = super(DateValidator, self)._convert_to_python(value)
        return value.date()


class RegexValidator(Validator):
    """
    Confirm the value matches a regular expression.

    `regex`
        A Python regular expression object, generated like
        ``re.compile('^\w+$')``
    """
    msgs = {
        'badregex': _('Invalid value'),
    }
    regex = None

    def _validate_python(self, value, state=None):
        if not self.regex.search(value):
            raise ValidationError('badregex', self)


class EmailValidator(RegexValidator):
    """
    Confirm the value is a valid email address.
    """
    msgs = {
        'badregex': ('bademail', _('Must be a valid email address')),
    }
    regex = re.compile('^[\w\-.]+@[\w\-.]+$')


class UrlValidator(RegexValidator):
    """
    Confirm the value is a valid URL.
    """
    msgs = {
        'regex': ('badurl', _('Must be a valid URL')),
    }
    regex = re.compile('^https?://', re.IGNORECASE)


class IpAddressValidator(Validator):
    """
    Confirm the value is a valid IP4 address, or network block.

    `allow_netblock`
        Allow the IP address to include a network block (default: False)

    `require_netblock`
        Require the IP address to include a network block (default: False)
    """
    allow_netblock = False
    require_netblock = False

    msgs = {
        'badipaddress': _('Must be a valid IP address'),
        'badnetblock': _('Must be a valid IP network block'),
    }
    regex = re.compile('^(\d+)\.(\d+)\.(\d+)\.(\d+)(/(\d+))?$')

    def _validate_python(self, value, state=None):
        m = self.regex.search(value)
        if not m or any(not(0 <= int(g) <= 255) for g in m.groups()[:4]):
            raise ValidationError('badipaddress', self)
        if m.group(6):
            if not self.allow_netblock:
                raise ValidationError('badipaddress', self)
            if not (0 <= int(m.group(6)) <= 32):
                raise ValidationError('badnetblock', self)
        elif self.require_netblock:
            raise ValidationError('badnetblock', self)


class UUIDValidator(Validator):
    """
    Confirm the value is a valid uuid and convert to uuid.UUID.
    """
    msgs = {
        'badregex': ('baduuid', _('Value not recognised as a UUID')),
    }

    regex = re.compile(\
               '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

    def _validate_python(self, value, state=None):
        if not self.regex.search(str(value)):
            raise ValidationError('badregex', self)

    def _convert_to_python(self, value, state=None):
        try:
            return uuid.UUID( "{%s}" % value )

        except ValueError:
            raise ValidationError('baduuid', self)

    def _convert_from_python(self, value, state=None):
        return str(value)


class MatchValidator(Validator):
    """Confirm a field matches another field

    `other_field`
        Name of the sibling field this must match
    `pass_on_invalid`
        Pass validation if sibling field is Invalid
    """
    msgs = {
        'mismatch': _("Must match $other_field_str"),
        'notfound': _("$other_field_str field is not found"),
        'invalid': _("$other_field_str field is invalid"),
    }

    def __init__(self, other_field, pass_on_invalid=False, **kw):
        super(MatchValidator, self).__init__(**kw)
        self.other_field = other_field
        self.pass_on_invalid = pass_on_invalid

    @property
    def other_field_str(self):
        return capitalize(util.name2label(self.other_field).lower())

    def _validate_python(self, value, state):
        if isinstance(state, dict):
            # Backward compatibility
            values = state
        else:
            values = state.full_dict

        if self.other_field not in values:
            raise ValidationError('notfound', self)

        other_value = values[self.other_field]

        if other_value is Invalid:
            if not self.pass_on_invalid:
                raise ValidationError('invalid', self)
        elif value != other_value:
            raise ValidationError('mismatch', self)

    def _is_empty(self, value):
        return self.required and super(MatchValidator, self)._is_empty(value)


class CompoundValidator(Validator):
    """ Base class for compound validators.

    Child classes :class:`Any` and :class:`All` take validators as arguments
    and use them to validate "value".  In case the validation fails, they
    raise a ValidationError with a compound message.

    >>> v = All(StringLengthValidator(max=50), EmailValidator, required=True)
    """

    def __init__(self, *args, **kw):
        super(CompoundValidator, self).__init__(**kw)

        self.validators = []
        for arg in args:
            if isinstance(arg, validator_classes):
                self.validators.append(arg)
            elif issubclass(arg, validator_classes):
                self.validators.append(arg())
            if getattr(arg, 'required', False):
                self.required = True


class All(CompoundValidator):
    """
    Confirm all validators passed as arguments are valid.
    """

    def _validate_python(self, value, state=None):
        msg = []
        for validator in self.validators:
            try:
                validator._validate_python(value, state)
            except ValidationError as e:
                msg.append(six.text_type(e))
        if msg:
            msgset = set()
            msg = ', '.join(m for m in msg
                if m not in msgset and not msgset.add(m))
            raise ValidationError(msg, self)


class Any(CompoundValidator):
    """
    Confirm at least one of the validators passed as arguments is valid.
    """

    def _validate_python(self, value, state=None):
        msg = []
        for validator in self.validators:
            try:
                validator._validate_python(value, state)
            except ValidationError as e:
                msg.append(six.text_type(e))
        if len(msg) == len(self.validators):
            msgset = set()
            msg = ', '.join(m for m in msg
                if m not in msgset and not msgset.add(m))
            raise ValidationError(msg, self)
