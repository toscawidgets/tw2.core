Validation
==========

One of the main features of any forms library is the vaidation of form input, e.g checking that an email address is valid, or that a user name is not already taken. If there are validation errors, these must be displayed to the user in a helpful way. Many validation tasks are common, so these should be easy for the developer, while less-common tasks are still possible.

**Conversion**

Validation is also responsible for conversion to and from python types. For example, the DateValidator takes a string from the form and produces a python date object. If it is unable to do this, that is a validation failure.

To keep related functionality together, validators also support coversion from python to string, for display. This should be complete, in that there are no python values that cause it to fail. It should also be precise, in that converting from python to string, and back again, should always give a value equal to the original python value. The converse is not always true, e.g. the string "1/2/2004" may be converted to a python date object, then back to "01/02/2004".

**Validation Errors**

When validation fails, the user should see the invalid values they entered. This is helpful in the case that a field is entered only slightly wrong, e.g. a number entered as "2,000" when commas are not allowed. In such cases, conversion to and from python may not be possible, so the value is kept as a string. Some widgets will not be able to display an invalid value (e.g. selection fields); this is fine, they just have to do the best they can.

When there is an error, whether valid fields could potentially normalise their value, by converting to python and back again. It was decided to use the original value in this case, although this may become a configurable option in the future.

In some cases, validation may encounter a major error, as if the web user has tampered with the HTML source. However, we can never be completely sure this is the case, perhaps they have a buggy browser, or caught the site in the middle of an upgrade. In these cases, validation will produce the most helpful error messages it can, which may just be "Your form submission was received corrupted; please try again."

**Required Fields**

If a field has no value, if defaults to ``None``. It is down to that field's validator to raise an error if the field is required. By default, fields are not required. It was considered to have a dedicated ``Missing`` class, but this was decided against, as ``None`` is already intended to convey the absence of data.

**Security Consideration**

When a widget is redisplayed after a validation failure, it's value is derived from unvalidated user input. So, all widgets must be "safe" for all input values. In practice, this is almost always the case without great care, so widgets are assumed to be safe. If a particular widget is not safe in this way, it must override :meth:`_validate` and set :attr:`value` to *None* in case of error.

**Validator Messages**

if msg is a tuple, it's (newname, msg)


Using Validators
----------------

There's two parts to using validators. First, specify validators in the widget definition, like this::

    class RegisterUser(twf.TableForm):
        validator = twc.MatchValidator('email', 'confirm_email')
        name = twf.TextField()
        email = twf.TextField(validator=twc.EmailValidator)
        confirm_email = twf.PasswordField()

You can specify a validator on any widget, either a class or an instance. Using an instance lets you pass parameters to the validator. You can code your own validator by subclassing :class:`tw2.core.Validator`. All validators have at least these parameters:

.. autoclass:: tw2.core.Validator

Second, when the form values are submitted, call :meth:`validate` on the outermost widget. Pass this a dictionary of the request parameters. It will call the same method on all contained widgets, and either return the validated data, with all conversions applied, or raise :class:`tw2.core.ValidationError`. In the case of a validation failure, it stores the invalid value and an error message on the affected widget.


FormEncode
----------

Earlier versions of ToscaWidgets used FormEncode for validation and there are good reasons for this. Some aspects of the design work very well, and FormEncode has a lot of clever validators, e.g. the ability to check that a post code is in the correct format for a number of different countries.

However, there are challenges making FormEncode and ToscaWidgets work together. For example, both libraries store the widget hierarchy internally. This makes implementing some features (e.g. ``strip_name`` and :class:`tw2.dynforms.HidingSingleSelectField`) difficult. There are different needs for the handling of unicode, leading ToscaWidgets to override some behaviour. Also, FormEncode just does not support client-side validation, a planned feature of ToscaWidgets 2.

ToscaWidgets 2 does not rely on FormEncode. However, developers can use FormEncode validators for individual fields. The API is compatible in that :meth:`to_python` and :meth:`from_python` are called for conversion, and :class:`formencode.Invalid` is caught.

Implementation
--------------

TBD
A two-pass approach is used internally, although this is invisible to the user. When :meth:`Widget.validate` is called (with validate=True), it automatically calls :meth:`Widget.unflatten_params`.

    unflatten_params decodes compound ids - use doc string

Then validate works recursively, using the widget hierarchy

There is a specific :class:`tw2.core.Invalid` marker, but this is only seen in a compound/repeating validator, if some of the children have failed validation.


**TBD** Messages


.. autoclass:: tw2.core.ValidationError


Available Validators
--------------------

.. autoclass:: tw2.core.Validator
.. autoclass:: tw2.core.LengthValidator
.. autoclass:: tw2.core.StringLengthValidator
.. autoclass:: tw2.core.ListLengthValidator
.. autoclass:: tw2.core.RangeValidator
.. autoclass:: tw2.core.IntValidator
.. autoclass:: tw2.core.OneOfValidator
.. autoclass:: tw2.core.DateValidator
.. autoclass:: tw2.core.DateTimeValidator
.. autoclass:: tw2.core.RegexValidator
.. autoclass:: tw2.core.EmailValidator
.. autoclass:: tw2.core.UrlValidator
.. autoclass:: tw2.core.IpAddressValidator
.. autoclass:: tw2.core.MatchValidator
