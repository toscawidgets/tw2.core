import core, re
try:
    import formencode
except ImportError:
    formencode = None

class Invalid(object):
    pass

class ValidationError(core.WidgetError):
    """Invalid data was encountered during validation.

    The constructor can be passed a short message name, which is looked up in
    a validator's :attr:`msgs` dictionary. Any values in this, like
    ``$val``` are substituted with that attribute from the validator. An
    explicit validator instance can be passed to the constructor, or this
    defaults to :class:`Validator` otherwise.
    """
    def __init__(self, msg, validator=None, widget=None):
        self.widget = widget
        if not validator:
            validator = Validator
        if msg in validator.msgs:
            msg = re.sub('\$(\w+)',
                lambda m: str(getattr(validator, m.group(1))),
                validator.msgs[msg])
        super(ValidationError, self).__init__(msg)


def catch_errors(fn):
    """
    """
    catch = ValidationError
    if formencode:
        catch = (catch, formencode.Invalid)
    def inner(self, *args, **kw):
        try:
            return fn(self, *args, **kw)
        except catch, e:
            if self:
                self.error_msg = str(e)
            raise ValidationError(str(e), widget=self)
    return inner


def unflatten_params(params):
    """This performs the first stage of validation. It takes a dictionary where
    some keys will be compound names, such as "form:subform:field" and converts
    this into a nested dict/list structure. This has been designed so it
    (should!) never raise an exception.
    """
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
    for k,v in dct.items():
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
            for b in bases:
                if hasattr(b, 'msgs'):
                    msgs.update(b.msgs)
            msgs.update(dct['msgs'])
            dct['msgs'] = msgs
        return type.__new__(meta, name, bases, dct)


# TBD: locked after init?
class Validator(object):
    """Base class for validators

    `required`
        Whether empty values are forbidden in this field. (default: False)

    `strip`
        Whether to strip leading and trailing space from the input, before
        any other validation. (default: True)

    `encoding`
        Input character set. All incoming strings are automatically decoded
        to Python Unicode objects, unless encoding is set to None.
        (default: 'utf-8')

    To create your own validators, sublass this class, and override any of:
    :meth:`to_python`, :meth:`validate_python`, or :meth:`from_python`.
    """
    __metaclass__ = ValidatorMeta

    msgs = {
        'required': 'Please enter a value',
        'decode': 'Received in the wrong character set',
        # TBD: is this the best place for these messages?
        'corrupt': 'The form submission was received corrupted; please try again',
        'childerror': 'Children of this widget have errors'
    }
    required = False
    strip = True
    encoding = 'utf-8'

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])

    def to_python(self, value, outer_call=None):
        if isinstance(value, basestring):
            try:
                if self.encoding:
                    value = value.decode(self.encoding)
            except UnicodeDecodeError, e:
                raise ValidationError('decode', self)
            if self.strip:
                value = value.strip()
        return value

    def validate_python(self, value, outer_call=None):
        if self.required and not value:
            raise ValidationError('required', self)

    def from_python(self, value, outer_call=None):
        return value

    def __repr__(self):
        _bool = ['False', 'True']
        return ("Validator(required=%s, strip=%s, encoding='%s')" %
            (_bool[int(self.required)], _bool[int(self.strip)], self.encoding))

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
        'tooshort': 'Value is too short',
        'toolong': 'Value is too long',
    }
    min = None
    max = None

    def validate_python(self, value):
        super(LengthValidator, self).validate_python
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
        'tooshort': 'Must be at least $min characters',
        'toolong': 'Cannot be longer than $max characters',
    }

class ListLengthValidator(LengthValidator):
    """
    Check a list is a suitable length. The only difference to LengthValidator
    is that the messages are worded differently.
    """

    msgs = {
        'tooshort': 'Pick at least $min',
        'toolong': 'Pick no more than $max',
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
        'toosmall': 'Must be at least $min',
        'toobig': 'Cannot be more than $max',
    }
    min = None
    max = None

    def validate_python(self, value):
        super(RangeValidator, self).validate_python(value)
        if self.min and value < self.min:
            raise ValidationError('toosmall', self)
        if self.max and value > self.max:
            raise ValidationError('toobig', self)


class IntValidator(RangeValidator):
    """
    Confirm the value is an integer. This is derived from :class:`RangeValidator`
    so `min` and `max` can be specified.
    """
    msgs = {
        'notint': 'Must be an integer',
    }

    def to_python(self, value):
        value = super(IntValidator, self).to_python(value)
        try:
            return int(value)
        except ValueError:
            raise ValidationError('notint', self)

    def from_python(self, value):
        return str(value)


class OneOfValidator(Validator):
    """
    Confirm the value is one of a list of acceptable values. This is useful for
    confirming that select fields have not been tampered with by a user.

    `values`
        Acceptable values
    """
    msgs = {
        'notinlist': 'Invalid value', # TBD: better message?
    }
    values = []

    def validate_python(self, value):
        super(OneOfValidator, self).validate_python(value)
        if value not in self.values:
            raise ValidationError('notinlist', self)


class DateValidator(RangeValidator):
    """
    Confirm the value is a valid date. This is derived from :class:`RangeValidator`
    so `min` and `max` can be specified.

    `format`
        The expected date format. The format must be specified using the same
        syntax as the Python strftime function.
    """
    msgs = {
        'notdate': 'Must follow date format $format_str',
        'toosmall': 'Cannot be earlier than $min_str',
        'toobig': 'Cannot be later than $max_str',
    }
    format = '%d/%m/%Y'

    format_tbl = {'d':'day', 'H':'hour', 'I':'hour', 'm':'month', 'M':'minute',
                  'S':'second', 'y':'year', 'Y':'year'}
    @property
    def format_str(self):
        return re.sub('%(.)', lambda m: format_tbl.get(m.group(1), ''), self.format)

    @property
    def min_str(self):
        return self.min.strftime(self.format)

    @property
    def max_str(self):
        return self.max.strftime(self.format)

    def to_python(self, value):
        value = super(DateValidator, self).to_python(value)
        try:
            date = time.strptime(value, self.format)
            return datetime.Date(date.tm_year, date.tm_month, date.tm_day)
        except ValueError:
            raise ValidationError('notdate', self)

    def from_python(self, value):
        return value.strftime(self.format)


class DateTimeValidator(DateValidator):
    """
    Confirm the value is a valid date and time; otherwise just like :class:`DateValidator`.
    """
    msgs = {
        'notdate': 'Must follow date/time format $format_str',
    }
    format = '%d/%m/%Y %h:%m'

    def to_python(self, value):
        value = super(DateTimeValidator, self).to_python(value)
        try:
            return datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError('notdate', self)

    def from_python(self, value):
        return value.strftime(self.format)


class RegexValidator(Validator):
    """
    Confirm the value matches a regular expression.

    `regex`
        A Python regular expression object, generated like ``re.compile('^\w+$')``
    """
    msgs = {
        'regex': 'Value must match regular expression',
    }
    regex = None

    def validate_python(self, value):
        super(RegexValidator, self).validate_python(value)
        if value and not self.regex.search(value):
            raise ValidationError('regex', self)


class EmailValidator(RegexValidator):
    """
    Confirm the value is a valid email address.
    """
    msgs = {
        'regex': 'Must be a valid email address',
    }
    regex = re.compile('^[\w\-.]+@[\w\-.]+$')


class UrlValidator(RegexValidator):
    """
    Confirm the value is a valid URL.
    """
    msgs = {
        'regex': 'Must be a valid URL',
    }
    regex = re.compile('^https?://', re.IGNORECASE)


class IpAddressValidator(Validator):
    """
    Confirm the value is a valid IP4 address.
    """
    msgs = {
        'ipaddress': 'Must be a valid IP address',
    }
    regex = re.compile('^(\d+)\.(\d+)\.(\d+)\.(\d+)$', re.IGNORECASE)
    def validate_python(self, value):
        m = self.regex.search(value)
        if not m or any(not(0 <= int(g) <= 255) for g in m.groups()):
            raise ValidationError('ipaddress', self)
