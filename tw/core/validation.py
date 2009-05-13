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
    def inner(self):
        try:
            return fn(self)
        except catch, e:
            self.err_msg = str(e)
            raise ValidationError(self.err_msg, widget=self)
    return inner


def unflatten_params(params):
    """This performs the first stage of validation. It takes a dictionary where
    some keys will be compound names, such as "form:subform:field" and converts
    this into a nested dict/list structure. Any values that are strings will be
    decoded to unicode. This has been designed to it (should!) never raise an
    exception.
    """
    out = {}
    for pname in params:
        dct = out
        elements = pname.split(':')
        for e in elements[:-1]:
            dct = dct.setdefault(e, {})
        dct[elements[-1]] = params[pname]

    number_re = re.compile('^\d+$')
    def numdict_to_list(dct):
        for k,v in dct.items():
            if isinstance(v, dict):
                numdict_to_list(v)
                if all(number_re.match(k) for k in v):
                    dct[k] = [v[x] for x in sorted(v, key=int)]
    numdict_to_list(out)
    return out


class ValidatorMeta(type):
    """Metaclass for :class:`Validator`.

    This makes the :attr:`msgs` dict copy from its base class. It also makes
    the :meth:`to_python`, :meth:`from_python` automatically call the base
    class method first.
    """
    def __new__(meta, name, bases, dct):
        if 'msgs' in dct:
            msgs = {}
            for b in bases:
                if hasattr(b, 'msgs'):
                    msgs.update(b.msgs)
            msgs.update(dct['msgs'])
            dct['msgs'] = msgs

        for meth in ('to_python', 'validate_python', 'from_python'):
            if meth in dct:
                if hasattr(bases[0], meth):
                    def wrapper(self, value, outer_call=True, meth=meth, method=dct[meth]):
                        value = getattr(bases[0], meth)(self, value, outer_call=False)
                        value = method(self, value)
                        if meth == 'to_python' and outer_call:
                            self.validate_python(value)
                        return value
                    dct[meth] = wrapper

        validator = type.__new__(meta, name, bases, dct)
        return validator


# TBD: locked after init?
class Validator(object):
    """Base class for validators

    TBD: describe msgs

    There are three parameters:

    `required`
        Whether empty values are forbidden in this field. If this is not
        specified, it defaults to the value specified in the parent. For
        widgets with no parent, it defaults to False.

    `strip`
        Whether to strip leading and trailing space from the input, before
        any other validation. (default: False)

    `encoding`
        Input character set. All incoming strings are automatically decoded
        to Python Unicode objects, unless encoding is set to None.
        (default: 'utf-8')

    To create your own validators, sublass this class, and override any of:
    :meth:`to_python`, :meth:`validate_python`, or :meth:`from_python`.
    There is a metaclass that makes these methods automatically call the base
    class method, so you do not need to use ``super`` in your methods.
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
        if self.required and not value:
            raise ValidationError('required', self)
        return value

    def validate_python(self, value, outer_call=None):
        pass

    def from_python(self, value, outer_call=None):
        return value

    def __repr__(self):
        _bool = ['False', 'True']
        return ("Validator(required=%s, strip=%s, encoding='%s')" %
            (_bool[int(self.required)], _bool[int(self.strip)], self.encoding))

class LengthValidator(Validator):
    msgs = {
        'tooshort': 'Value is too short',
        'toolong': 'Value is too long',
    }
    min = None
    max = None

    def validate_python(self, value):
        if self.min and len(value) < self.min:
            raise ValidationError('tooshort', self)
        if self.max and len(value) > self.max:
            raise ValidationError('toolong', self)

class StringLengthValidator(LengthValidator):
    msgs = {
        'tooshort': 'Must be at least $min characters',
        'toolong': 'Cannot be longer than $max characters',
    }

class ListLengthValidator(LengthValidator):
    msgs = {
        'tooshort': 'Pick at least $min',
        'toolong': 'Pick no more than $max',
    }


class RegexValidator(Validator):
    msgs = {
        'regex': 'Value must match regular expression',
    }
    regex = None

    def validate_python(self, value):
        if not self.regex.search(value):
            raise ValidationError('regex', self)


class RangeValidator(Validator):
    msgs = {
        'toosmall': 'Must be at least $min',
        'toobig': 'Cannot be more than $max',
    }
    min = None
    max = None

    def validate_python(self, value):
        if self.min and value < self.min:
            raise ValidationError('toosmall', self)
        if self.max and value > self.max:
            raise ValidationError('toobig', self)


class IntValidator(RangeValidator):
    msgs = {
        'notint': 'Must be an integer',
    }

    def to_python(self, value):
        try:
            return int(value)
        except ValueError:
            raise ValidationError('notint', self)

    def from_python(self, value):
        return str(value)


class OneOfValidator(Validator):
    msgs = {
        'notinlist': 'Invalid value', # TBD: better message?
    }
    values = []

    def validate_python(self, value):
        if value not in self.values:
            raise ValidationError('notinlist', self)


class DateValidator(RangeValidator):
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
        try:
            date = time.strptime(value, self.format)
            return datetime.Date(date.tm_year, date.tm_month, date.tm_day)
        except ValueError:
            raise ValidationError('notdate', self)

    def from_python(self, value):
        return value.strftime(self.format)


class DateTimeValidator(DateValidator):
    msgs = {
        'notdate': 'Must follow date/time format $format_str',
    }
    format = '%d/%m/%Y %h:%m'

    def to_python(self, value):
        try:
            return datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError('notdate', self)

    def from_python(self, value):
        return value.strftime(self.format)


# email
# url
# ip address
