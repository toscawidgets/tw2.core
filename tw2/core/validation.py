import core, re, util, string, time, datetime, copy, decorator, webob

# This hack helps work with different versions of WebOb
if not hasattr(webob, 'MultiDict'):
    webob.MultiDict = webob.multidict.MultiDict
if not hasattr(webob, 'UnicodeMultiDict'):
    webob.UnicodeMultiDict = webob.multidict.UnicodeMultiDict

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
        pass


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
        msg = re.sub('\$(\w+)',
                lambda m: str(getattr(validator, m.group(1))), msg)
        super(ValidationError, self).__init__(msg)
        
    @property
    def message(self):
        """ Added for backwards compatibility.  Synonymous with `msg` """
        return self.msg


def safe_validate(validator, value):
    try:
        value = validator.to_python(value)
        validator.validate_python(value)
        return value
    except ValidationError:
        return Invalid


catch = ValidationError
if formencode:
    catch = formencode.Invalid

@decorator.decorator
def catch_errors(fn, self, *args, **kw):
    try:
        d = fn(self, *args, **kw)
        return d
    except catch, e:
        if self:
            self.error_msg = str(e)
        raise ValidationError(str(e), widget=self)


def unflatten_params(params):
    """This performs the first stage of validation. It takes a dictionary where
    some keys will be compound names, such as "form:subform:field" and converts
    this into a nested dict/list structure. It also performs unicode decoding,
    with the encoding specified in the middleware config.
    """
    if ( isinstance(params, webob.MultiDict) or
         isinstance(params, webob.UnicodeMultiDict) ):
        params = params.mixed()    
    mw = core.request_local().get('middleware')
    enc = mw.config.encoding if mw else 'utf-8'
    try:
        for p in params:
            if isinstance(params[p], str):
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
            rewrites = {}
            for b in bases:
                if hasattr(b, 'msgs'):
                    msgs.update(b.msgs)
            msgs.update(dct['msgs'])
            for m,d in msgs.items():
                if isinstance(d, tuple):
                    msgs[d[0]] = d[1]
                    rewrites[m] = d[0]
                    del msgs[m]
            dct['msgs'] = msgs
            dct['msg_rewrites'] = rewrites
        return type.__new__(meta, name, bases, dct)


class Validator(object):
    """Base class for validators

    `required`
        Whether empty values are forbidden in this field. (default: False)

    `strip`
        Whether to strip leading and trailing space from the input, before
        any other validation. (default: True)

    To create your own validators, sublass this class, and override any of:
    :meth:`to_python`, :meth:`validate_python`, or :meth:`from_python`.
    """
    __metaclass__ = ValidatorMeta

    msgs = {
        'required': 'Enter a value',
        'decode': 'Received in the wrong character set; should be $encoding',
        'corrupt': 'The form submission was received corrupted; please try again',
        'childerror': '' # Children of this widget have errors
    }
    required = False
    strip = True

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw[k])

    def to_python(self, value):
        if self.required and (value is None or not value):
            raise ValidationError('required', self)
        if isinstance(value, basestring) and self.strip:
            value = value.strip()
        return value

    def validate_python(self, value, state=None):
        if self.required and not value:
            raise ValidationError('required', self)

    def from_python(self, value):
        return value

    def __repr__(self):
        _bool = ['False', 'True']
        return ("Validator(required=%s, strip=%s)" %
            (_bool[int(self.required)], _bool[int(self.strip)]))

    def clone(self, **kw):
        nself = copy.copy(self)
        for k in kw:
            setattr(nself, k, kw[k])
        return nself


class BlankValidator(Validator):
    """
    Always returns EmptyField. This is the default for hidden fields,
    so their values are not included in validated data.
    """
    def to_python(self, value):
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
        'tooshort': 'Value is too short',
        'toolong': 'Value is too long',
    }
    min = None
    max = None

    def validate_python(self, value, state=None):
        super(LengthValidator, self).validate_python(value, state)
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
        'tooshort': ('string_tooshort', 'Must be at least $min characters'),
        'toolong': ('string_toolong', 'Cannot be longer than $max characters'),
    }

class ListLengthValidator(LengthValidator):
    """
    Check a list is a suitable length. The only difference to LengthValidator
    is that the messages are worded differently.
    """

    msgs = {
        'tooshort': ('list_tooshort', 'Select at least $min'),
        'toolong': ('list_toolong', 'Select no more than $max'),
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

    def validate_python(self, value, state=None):
        super(RangeValidator, self).validate_python(value, state)
        if self.min is not None and value < self.min:
            raise ValidationError('toosmall', self)
        if self.max is not None and value > self.max:
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
            if value is None or str(value) == '':
                return None
            else:
                return int(value)
        except ValueError:
            raise ValidationError('notint', self)

    def validate_python(self, value, state=None):
        # avoid super().validate_python, as it sees int(0) as missing
		# TODO -- TBD -- is this still necessary after epic merge?
        value = self.to_python(value) # TBD: I wanted to avoid this; needed to make unit tests pass
        if self.required and value is None:
            raise ValidationError('required', self)
        if value is not None:
            if self.min and value < self.min:
                raise ValidationError('toosmall', self)
            if self.max and value > self.max:
                raise ValidationError('toobig', self)

    def from_python(self, value):
        if value is None:
            return None
        else:
            return str(value)


class BoolValidator(RangeValidator):
    """
    Convert a value to a boolean. This is particularly intended to handle
    check boxes.
    """
    msgs = {
        'required': ('bool_required', 'You must select this')
    }
    def to_python(self, value):
        value = super(BoolValidator, self).to_python(value)
        return str(value).lower() in ('on', 'yes', 'true', '1')


class OneOfValidator(Validator):
    """
    Confirm the value is one of a list of acceptable values. This is useful for
    confirming that select fields have not been tampered with by a user.

    `values`
        Acceptable values
    """
    msgs = {
        'notinlist': 'Invalid value',
    }
    values = []

    def validate_python(self, value, state=None):
        super(OneOfValidator, self).validate_python(value, state)
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
        'baddate': 'Must follow date format $format_str',
        'toosmall': ('date_toosmall', 'Cannot be earlier than $min_str'),
        'toobig': ('date_toobig', 'Cannot be later than $max_str'),
    }
    format = '%d/%m/%Y'

    format_tbl = {'d':'day', 'H':'hour', 'I':'hour', 'm':'month', 'M':'minute',
                  'S':'second', 'y':'year', 'Y':'year'}
    @property
    def format_str(self):
        return re.sub('%(.)', lambda m: self.format_tbl.get(m.group(1), ''), self.format)

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
            return datetime.date(date.tm_year, date.tm_mon, date.tm_mday)
        except ValueError:
            raise ValidationError('baddate', self)

    def from_python(self, value):
        return value and value.strftime(self.format) or ''


class DateTimeValidator(DateValidator):
    """
    Confirm the value is a valid date and time; otherwise just like :class:`DateValidator`.
    """
    msgs = {
        'baddate': ('baddatetime', 'Must follow date/time format $format_str'),
    }
    format = '%d/%m/%Y %H:%M'

    def to_python(self, value):
        if value is None:
            return value
        try:
            return datetime.datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError('baddate', self)


class RegexValidator(Validator):
    """
    Confirm the value matches a regular expression.

    `regex`
        A Python regular expression object, generated like ``re.compile('^\w+$')``
    """
    msgs = {
        'badregex': 'Invalid value',
    }
    regex = None

    def validate_python(self, value, state=None):
        super(RegexValidator, self).validate_python(value, state)
        if value and not self.regex.search(value):
            raise ValidationError('badregex', self)


class EmailValidator(RegexValidator):
    """
    Confirm the value is a valid email address.
    """
    msgs = {
        'badregex': ('bademail', 'Must be a valid email address'),
    }
    regex = re.compile('^[\w\-.]+@[\w\-.]+$')


class UrlValidator(RegexValidator):
    """
    Confirm the value is a valid URL.
    """
    msgs = {
        'regex': ('badurl', 'Must be a valid URL'),
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
        'badipaddress': 'Must be a valid IP address',
        'badnetblock': 'Must be a valid IP network block',
    }
    regex = re.compile('^(\d+)\.(\d+)\.(\d+)\.(\d+)(/(\d+))?$')
    def validate_python(self, value, state=None):
        if value:
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


class MatchValidator(Validator):
    """Confirm a field matches another field
    
    `other_field`
        Name of the sibling field this must match
    """
    msgs = {
        'mismatch': "Must match $other_field_str"
    }

    def __init__(self, other_field, **kw):
        super(MatchValidator, self).__init__(**kw)
        self.other_field = other_field

    @property
    def other_field_str(self):
        return string.capitalize(util.name2label(self.other_field).lower())

    def validate_python(self, value, state):
        super(MatchValidator, self).validate_python(value, state)        
        if value != state[self.other_field]:
            raise ValidationError('mismatch', self)
