.. _validation:

Validation
==========

ToscaWidgets provides validation support for all the data
that needs to be displayed into widgets or that has to
come from submitted forms.

Setting a validator for a widget (or a form field) can
be done through the :attr:`tw2.core.Widget.validator` param.

Validators are typically used in the context of forms
and can be used both to tell ToscaWidgets how
a python object should be displayed in HTML result::

    >>> import tw2.core as twc
    >>> import tw2.forms as twf
    >>>
    >>> w = twf.TextField(validator=twc.validation.DateValidator(format="%Y/%m/%d"))
    >>> w.display(datetime.datetime.utcnow())
    Markup('<input value="2019/04/04" type="text"/>')

Or to tell ToscaWidgets how the data coming from a
submitted form should be converted into Python::

    >>> class MyDateForm(twf.Form):
    ...   class child(twf.TableLayout):
    ...     date = twf.TextField(validator=twc.validation.DateValidator(format="%Y/%m/%d"))
    ... 
    >>> MyDateForm.validate({'date': '2019/5/3'})
    {'date': datetime.date(2019, 5, 3)}

Validators
----------

A validator is a class in charge of two major concerns:

* Converting data from the web to python and back to the web
* Validating that the data is what you expected.

Both those step are performed through two methods:

:meth:`tw2.core.validation.Validator.to_python` which is
in charge of converting data from the web to Python::

    >>> validator = twc.validation.DateValidator(required=True, format="%Y/%m/%d")
    >>> validator.to_python('2019/10/3')
    datetime.date(2019, 10, 3)

and :meth:`tw2.core.validation.Validator.from_python` which
is in charge of converting data from Python to be displahyed
on a web page::

    >>> validator.from_python(datetime.datetime.utcnow())
    "2019/04/04"

When converting data *to python* (so for data submitted
from the web to your web application) the validator does three
steps:

1. Ensures that the data is not empty through :meth:`tw2.core.validation.Validator._is_empty` if ``required=True`` was provided
2. Converts data to Python through :meth:`tw2.core.validation.Validator._convert_to_python`
3. Validates that the converted data matches what you expected through :meth:`tw2.core.validation.Validator._validate_python`

All those three methods (``is_empty``, ``_convert_to_python`` and ``_validate_python``)
can be specialised in subclasses to implement your own validators.

For example the :class:`tw2.core.validation.IntValidator` takes care
of converting the incoming text to intergers::

    >>> twc.validation.IntValidator().to_python("5")
    5

but also takes care of validating that it's within an expected range::

    >>> twc.validation.IntValidator(min=1).to_python("0")
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 236, in to_python
        self._validate_python(value, state)
    File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 376, in _validate_python
        raise ValidationError('toosmall', self)
    tw2.core.validation.ValidationError: Must be at least 1

Custom Validators
-----------------

You can write your own validators by subclassing :class:`tw2.core.validation.Validator`.

Those should *at least* implement the custom conversion part, to tell
toscawidgets how to convert the incoming data to the type you expect::

    class TwoNumbersValidator(twc.validation.Validator):    
        def _convert_to_python(self, value, state=None):
            try:
                return [int(v) for v in value.split(',')]
            except ValueError:
                raise twc.validation.ValidationError("Must be integers", self)
            except Exception:
                raise twc.validation.ValidationError("corrupt", self)

This is already enough to be able to convert the incoming
data to a list of numbers::

    >>> TwoNumbersValidator().to_python("5,3")
    [5, 3]

and to detect that numbers were actually submitted::

    >>> TwoNumbersValidator().to_python("5, allo")
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 235, in to_python
            value = self._convert_to_python(value, state)
        File "<stdin>", line 6, in _convert_to_python
    tw2.core.validation.ValidationError: Must be integers

and to detect malformed inputs::

    >>> TwoNumbersValidator().to_python(datetime.datetime.utcnow())
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 235, in to_python
            value = self._convert_to_python(value, state)
        File "<stdin>", line 8, in _convert_to_python
    tw2.core.validation.ValidationError: Form submission received corrupted; please try again

But it doesn't perform validation on the converted data.
It doesn't ensure that what was provided are really two numbers::

    >>> TwoNumbersValidator().to_python("5")
    [5]

To do so we need to implement the validation part of the validator,
which is done through ``_validate_python``::

    class TwoNumbersValidator(twc.validation.Validator):    
        def _convert_to_python(self, value, state=None):
            try:
                return [int(v) for v in value.split(',')]
            except ValueError:
                raise twc.validation.ValidationError("Must be integers", self)
            except Exception:
                raise twc.validation.ValidationError("corrupt", self)
        
        def _validate_python(self, value, state=None):
            if len(value) != 2:
                raise twc.validation.ValidationError("Must be two numbers", self)

To finally provide coverage for the case where a single number
(or more than two numbers) were provided::

    >>> TwoNumbersValidator().to_python("5")
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 236, in to_python
            self._validate_python(value, state)
        File "<stdin>", line 11, in _validate_python
    tw2.core.validation.ValidationError: Must be two numbers

You will notice by the way, that empty values won't cause validation errors::

    >>> v = TwoNumbersValidator().to_python("")

Those will be converted to ``None``::

    >>> print(v)
    None

Because by default validators have ``required=False`` which means that
missing values are perfectly fine.

If you want to prevent that behaviour you can provide ``required=True``
to the validator::

    >>> TwoNumbersValidator(required=True).to_python("")
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 231, in to_python
            raise ValidationError('required', self)
    tw2.core.validation.ValidationError: Enter a value

Internationalization
--------------------

Validator error messages can be translated through the usage of
the ``msgs`` lookup dictionary.

The ``msgs`` dictionary is a map from keywords to translated 
strings and it's used by ToscaWidgets to know which message
to show to users::

    from tw2.core.i18n import tw2_translation_string

    class FloatValidator(twc.Validator):
        msgs = {
            "notfloat": tw2_translation_string("Not a floating point number")
        }

        def _convert_to_python(self, value, state):
            try:
                return float(value)
            except ValueError:
                raise twc.validation.ValidationError("notfloat", self)

You will see that when validation fails, the ``"notfloat"`` key is
looked up into ``msgs`` to find the proper message::

    >>> FloatValidator().to_python("Hello")
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 235, in to_python
            value = self._convert_to_python(value, state)
        File "<stdin>", line 9, in _convert_to_python
    tw2.core.validation.ValidationError: Not a floating point number

The entry in ``msgs`` is then wrapped in a :meth:`tw2.core.i18n.tw2_translation_string`
call to ensure it gets translated using the translated that was configured
in :class:`tw2.core.middleware.TwMiddleware` options.

.. note::

    :meth:`tw2.core.i18n.tw2_translation_string` is also available as
    ``tw2.core.i18n._`` so that frameworks that automate translatable
    strings collection like Babel can more easily find strings that
    need translation in ToscaWidgets validators.

The other purpose of ``msgs`` is to allow users of your validator
to customise their error messages::

    >>> FloatValidator(msgs={"notfloat": "Ahah! Gotcha!"}).to_python("Hello")
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 235, in to_python
            value = self._convert_to_python(value, state)
        File "<stdin>", line 9, in _convert_to_python
    tw2.core.validation.ValidationError: Ahah! Gotcha!

In such case (when ``msgs`` are customised) translation of the messages
is up to the user customising them. Who might want to ensure the new provided
messages are still wrapped in :meth:`tw2.core.i18n.tw2_translation_string`.

Builtin Validators
------------------

.. automodule:: tw2.core.validation
    :members:
    :member-order: bysource
    :exclude-members: BaseValidationError, ValidatorMeta, 
    :no-inherited-members: