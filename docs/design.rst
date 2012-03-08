Design
------

Widget Overview
===============

The main purpose of a widget is to display a functional control within an HTML page. A widget has a template to generate its own HTML, and a set of parameters that control how it will be displayed. It can also reference resources - JavaScript or CSS files that support the widget.

When defining Widgets, some parameters with be static - they will stay constant for the whole lifetime of the application. Some parameters are dynamic - they may change for every request. To ensure thread-safety, a separate widget instance is created for every request, and dynamic parameters are only set on an instance. Static parameters are set by subclassing a widget. For example::

    # Initialisation
    class MyWidget(Widget):
        id = 'myid'

    # In a request
    my_widget = MyWidget.req()
    my_widget.value = 'my value'

To make initialisation more concise, the ``__new__`` method on ``Widget`` is overriden, so it creates subclasses, rather than instances. The following code is equivalent to that above::

    # Initialisation
    MyWidget = Widget(id='myid')

In practice, you will rarely need to explictly create an instance, using ``req()``. If the ``display`` or ``validate`` methods are called on a Widget class, they automatically create an instance. For example, the following are equivalent::

    # Explicit creation
    my_widget = MyWidget.req()
    my_widget.value = 'my value'
    my_widget.display()

    # Implicit creation
    MyWidget.display(value='my value')


Parameters
~~~~~~~~~~

The parameters are how the user of the widget controls its display and behaviour. Parameters exist primarily for documentation purposes, although they do have some run-time effects. When creating widgets, it's important to decide on a convenient set of parameters for the user of the widget, and to document these.

A parameter definition looks like this::

    import tw2.core as twc
    class MyTextField(twc.Widget):
        size = twc.Param('The size of the field', default=30)
        validator = twc.LengthValidator(max=30)
        highlight = twc.Variable('Region to highlight')

In this case, :class:`TextField` gets all the parameters of its base class, :class:`tw2.core.widget` and defines a new parameter - :attr:`size`. A widget can also override parameter in its base class, either with another :class:`tw2.core.Param` instance, or a new default value.

.. autoclass:: tw2.core.Param
.. autoclass:: tw2.core.Variable
.. autoclass:: tw2.core.ChildParam
.. autoclass:: tw2.core.ChildVariable


Code Hooks
~~~~~~~~~~

Subclasses of Widget can override the following methods. It is not recommended to override any other methods, e.g. display, validate, __init__.

.. automethod:: tw2.core.widgets.Widget.post_define
.. automethod:: tw2.core.widgets.Widget.prepare
.. automethod:: tw2.core.widgets.Widget.generate_output

**Mutable Members**

If a widget's :meth:`prepare` method modifies a mutable member on the widget, it must take care not to modify a class member, as this is not thread safe. In general, the code should call :attr:`self.safe_modify(member_name)`, which detects class members and creates a copy on the instance. Users of widgets should be aware that if a mutable is set on an instance, the widget may modify this. The most common case of a mutable member is :attr:`attrs`. While this arrangement is thread-safe and reasonably simple, copying may be bad for performance. In some cases, widgets may deliberately decide not to call :meth:`safe_modify`, if the implications of this are understood.


Widget Hierarchy
================

Widgets can be arranged in a hierarchy. This is useful for applications like layouts, where the layout will be a parent widget and fields will be children of this. There are four roles a widget can take in the hierarchy, depending on the base class used:

.. autoclass:: tw2.core.Widget
.. autoclass:: tw2.core.CompoundWidget
.. autoclass:: tw2.core.RepeatingWidget
.. autoclass:: tw2.core.DisplayOnlyWidget

**Value Propagation**

An important feature of the hierarchy is value propagation. When the value is set for a compound or repeating widget, this causes the value to be set for the child widgets. In general, a leaf widget takes a scalar type as a value, a compound widget takes a dict or an  object, and a repeating widget takes a list.

The hierarchy also affects the generation of compound ids, and validation.

**Identifier**

In general, a widget needs to have an identifier. Without an id, it cannot participate in value propagation or validation, and it does not get an HTML id attribute. There are some exceptions to this:

 * Some widgets do not need an id (e.g. Label, Spacer) and provide a default id of None.
 * The child of a RepeatingWidget must not have an id.
 * An id can be specified either on a DisplayOnlyWidget, or it's child, but not both. The widget that does not have the id specified automatically picks it up from the other.

Compound IDs are formed by joining the widget's id with those of its ancestors. These are used in two situations:

 * For the HTML id attribute, and also the name attribute for form fields
 * For the URL path a controller widget is registered at

The separator is a colon (:), resulting in compound ids like "form:sub_form:field". **Note** this causes issues with CSS and will be changed shortly, and made configurable.

In generel, the id on a DisplayOnlyWidget is not included in the compound id. However, when generating the compound id for a DisplayOnlyWidget, the id is included. In addition *id_suffix* is appended, to avoid generating duplicate IDs. The *id_suffix* is not appended for URL paths, to keep the paths short. There is a risk of duplicate IDs, but this is not expected to be a problem in practice.

For children of a RepeatingWidget, the repetition is used instead of the id, for generating the compound HTML id. For the URL path, the element is skipped entirely.


**Deep Children**

This is a feature that helps have a form layout that doesn't exactly match the database layout. For example, we might have a sinlge database table, with fields like title, customer, start_date, end_date. We want to display this in a Form that's broken up into two FieldSets. Without deep children, the FieldSets would have to have ids, and field makes would be dotted, like info.title. The deep children feature lets us set the id to None::

    class MyForm(twf.Form):
        class child(twc.CompoundWidget):
            class info(twf.TableFieldSet):
                id = None
                title = twf.TextField()
                customer = twf.TextField()
            class dates(twf.TableFieldSet):
                id = None
                start_date = twf.TextField()
                end_date = twf.TextField()

When a value like ``{'title': 'my title'}`` is passed to MyForm, this will propagate correctly.


Template
========

Every widget can have a template. ToscaWidgets aims to support any templating engine that support the ``buffet`` interface, which is an initiative by the TurboGears project to create a standard interface for template libraries. In practice, there are more differences between template engines than the buffet interface standardises. So, ToscaWidgets has some template-language hooks, and support is primarily for: Genshi, Mako, Kid and Cheetah.

The :attr:`template` parameter takes the form ``engine_name:template_path``. The ``engine_name`` is the name that the template engine defines in the ``python.templating.engines`` entry point, e.g. ``genshi`` or ``mako``. The ``template_path`` is a string the engine can use to locate the template; usually this is dot-notation that mimics the semantics of Python's import statement, e.g. ``myapp.templates.mytemplate``. Genshi templates allow specifications like ``./template.html`` which is beneficial for simple applications.

It is also possible to allow your widget to utilize multiple templates, or to have TW2 support any template language you provide a template for.  To do this, simply leave the name of the template engine off of the template parameter, and TW2 will select the appropriate template, based on specifications in the TW2 middleware.

For instance, you might have a form.mak and a form.html template (mako and genshi). TW2 will render the mako template if mako is listed ahead of genshi in the middleware config's ``preferred_rendering_engines``.  See the documentation regarding :ref:`middleware` for more information on how to set up your middleware for desired output.

.. autoclass:: tw2.core.template.EngineManager
   :members: render, _get_adaptor_renderer


Non-template Output
===================

Instead of using a template, a widget can also override the ``generate_output`` method. This function generates the HTML output for a widget; by default, it renders the widget's template as described in the previous section, but can be overridden by any function that returns a string of HTML.


Resources
=========

Widgets often need to access resources, such as JavaScript or CSS files. A key feature of widgets is the ability to automatically serve such resources, and insert links into appropriate sections of the page, e.g. ``<HEAD>``. There are several parts to this:

 * Widgets can define resources they use, using the :attr:`resources` parameter.
 * When a Widget is displayed, it registers resources in request-local storage, and with the resource server.
 * The resource injection middleware detects resources in request-local storage, and rewrites the generated page to include appropriate links.
 * The resource server middleware serves static files used by widgets
 * Widgets can also access resources at display time, e.g. to get links
 * Resources can themselves declare dependency on other resources, e.g.
   jquery-ui.js depends on jquery.js and must be included on the page
   subsequently.

**Defining Resources**

To define a resource, just add a :class:`tw2.core.Resource` subclass to the widget's :attr:`resources` parameter. It is also possible to append to :attr:`resources` from within the :meth:`prepare` method. The following resource types are available:

.. autoclass:: tw2.core.CSSLink
.. autoclass:: tw2.core.CSSSource
.. autoclass:: tw2.core.JSLink
.. autoclass:: tw2.core.JSSource
.. autoclass:: tw2.core.JSFuncCall

Resources are widgets, but follow a slightly different lifecycle. Resource subclasses are passed into the :attr:`resources` parameter. An instance is created for each request, but this is only done at the time of the parent Widget's :meth:`display` method. This gives widgets a chance to add dynamic resources in their :meth:`prepare` method.

**Deploying Resources**

If running behind mod_wsgi, tw2 resource provisioning will typically fail.
Resources are only served when they are registered with the request-local
thread, and resources are only registered when their dependant widget is
displayed in a request.  An initial page request may make available resource
``A``, but the subsequent request to actually retrieve resource ``A`` will not
have that resource registered.

To solve this problem (and to introduce a speed-up for production deployment),
Toscawidgets2 provides an ``archive_tw2_resources`` distutils command::

    $ python setup.py archive_tw2_resources \
        --distributions=myapplication \
        --output=/var/www/myapplication

.. _middleware:

Middleware
==========


The WSGI middleware has three functions:

 * Request-local storage
 * Configuration
 * Resource injection

**Configuration**

In general, ToscaWidgets configuration is done on the middleware instance. At the beginning of each request, the middleware stores a reference to itself in request-local storage. So, during a request, a widget can consult request-local storage, and get the configuration for the middleware active in that request. This allows multiple applications to use ToscaWidgets, with different configurations, in a single Python environment.

Configuration is passed as keyword arguments to the middleware constructor. The available parameters are:

.. autoclass:: tw2.core.middleware.Config


Declarative Instantiation
=========================

Instantiating compound widgets can result in less-than-beautiful code. To help alleviate this, widgets can be defined declaratively, and this is the recommended approach. A definition looks like this::

    class MovieForm(twf.TableForm):
        id = twf.HiddenField()
        year = twf.TextField()
        desc = twf.TextArea(rows=5)

Any class members that are subclasses of Widget become children. All the children get their ``id`` from the name of the member variable. Note: it is important that all children are defined like ``id = twf.HiddenField()`` and not ``id = twf.HiddenField``. Otherwise, the order of the children will not be preserved.

It is possible to define children that have the same name as parameters, using this syntax. However, doing so does prevent a widget overriding a parameter, and defining a child with the same name. If you need to do this, you must use a throwaway name for the member variable, and specify the id explicitly, e.g.::

    class MovieForm(twf.TableForm):
        resources = [my_resource]
        id = twf.HiddenField()
        noname = twf.TextArea(id='resources')


**Nesting and Inheritence**

Nested declarative definitions can be used, like this::

    class MyForm(twf.Form):
        class child(twf.TableLayout):
            b = twf.TextArea()
            x = twf.Label(text='this is a test')
            c = twf.TextField()

Inheritence is supported - a subclass gets the children from the base class, plus any defined on the subclass. If there's a name clash, the subclass takes priority. Multiple inheritence resolves name clashes in a similar way. For example::

    class MyFields(twc.CompoundWidget):
        b = twf.TextArea()
        x = twf.Label(text='this is a test')
        c = twf.TextField()

    class TableFields(MyFields, twf.TableLayout):
        pass

    class ListFields(MyFields, twf.ListLayout):
        b = twf.TextField()

**Proxying children**

Without this feature, double nesting of classes is often necessary, e.g.::

    class MyForm(twf.Form):
        class child(twf.TableLayout):
            b = twf.TextArea()

Proxying children means that if :class:`RepeatingWidget` or :class:`DisplayOnlyWidget` have :attr:`children` set, this is passed to their :attr:`child`. The following is equivalent to the definition above::

    class MyForm(twf.Form):
        child = twf.TableLayout()
        b = twf.TextArea()

And this is used by classes like :class:`TableForm` and :class:`TableFieldSet` to allow the user more concise widget definitions::

    class MyForm(twf.TableForm):
        b = twf.TextArea()


**Automatic ID**

Sub classes of :class:`Page` that do not have an id, will have the id automatically set to the name of the class. This can be disabled by setting :attr:`_no_autoid` on the class. This only affects that specific class, not any subclasses.


Widgets as Controllers
======================

Sometimes widgets will want to define controller methods. This is particularly useful for Ajax widgets. Any widget can have a :meth:`request` method, which is called with a WebOb :class:`Request` object, and must return a WebOb :class:`Response` object, like this::

    class MyWidget(twc.Widget):
        id = 'my_widget'
        @classmethod
        def request(cls, req):
            resp = webob.Response(request=req, content_type="text/html; charset=UTF8")
            # ...
            return resp

For the :meth:`request` method to be called, the widget must be registered with the :class:`ControllersApp` in the middleware. By default, the path is constructed from /controllers/, and the widget's id. A request to /controllers/ refers to a widget with id ``index``. You can specify :attr:`controllers_prefix` in the configuration.

For convenience, widgets that have a :meth:`request` method, and an :attr:`id` will be registered automatically. By default, this uses a global :class:`ControllersApp` instance, which is also the default controllers for :func:`make_middleware`. If you want to use multiple controller applications in a single python instance, you will need to override this.

You can also manually register widgets::

    twc.core.register_controller(MyWidget, 'mywidget')

**Methods to override**

    `view_request`
        Instance method - get self and req. load from db

    `validated_request`
        Class method - get cls and validated data

    `ajax_request`
        Return python data that is automatically converted to an ajax response


Validation
==========

One of the main features of any forms library is the vaidation of form input, e.g checking that an email address is valid, or that a user name is not already taken. If there are validation errors, these must be displayed to the user in a helpful way. Many validation tasks are common, so these should be easy for the developer, while less-common tasks are still possible.

**Conversion**

Validation is also responsible for conversion to and from python types. For example, the DateValidator takes a string from the form and produces a python date object. If it is unable to do this, that is a validation failure.

To keep related functionality together, validators also support coversion from python to string, for display. This should be complete, in that there are no python values that cause it to fail. It should also be precise, in that converting from python to string, and back again, should always give a value equal to the original python value. The converse is not always true, e.g. the string "1/2/2004" may be converted to a python date object, then back to "01/02/2004".

**Validation Errors**

When there is an error, all fields should still be validated and multiple errors displayed, rather than stopping after the first error.

When validation fails, the user should see the invalid values they entered. This is helpful in the case that a field is entered only slightly wrong, e.g. a number entered as "2,000" when commas are not allowed. In such cases, conversion to and from python may not be possible, so the value is kept as a string. Some widgets will not be able to display an invalid value (e.g. selection fields); this is fine, they just have to do the best they can.

When there is an error is some fields, other valid fields can potentially normalise their value, by converting to python and back again (e.g. 01234 -> 1234). However, it was decided to use the original value in this case.

In some cases, validation may encounter a major error, as if the web user has tampered with the HTML source. However, we can never be completely sure this is the case, perhaps they have a buggy browser, or caught the site in the middle of an upgrade. In these cases, validation will produce the most helpful error messages it can, but not attempt to identify which field is at fault, nor redisplay invalid values.

**Required Fields**

If a field has no value, if defaults to ``None``. It is down to that field's validator to raise an error if the field is required. By default, fields are not required. It was considered to have a dedicated ``Missing`` class, but this was decided against, as ``None`` is already intended to convey the absence of data.

**Security Consideration**

When a widget is redisplayed after a validation failure, it's value is derived from unvalidated user input. This means widgets must be "safe" for all input values. In practice, this is almost always the case without great care, so widgets are assumed to be safe. 

.. warning::
    If a particular widget is not safe in this way, it must override :meth:`_validate` and set :attr:`value` to *None* in case of error.

**Validation Messages**

When validation fails, the validator raises :class:`ValidationError`. This must be passed the short message name, e.g. "required". Each validator has a dictionary mapping short names to messages that are presented to the user, e.g.::

    msgs = {
        'tooshort': 'Value is too short',
        'toolong': 'Value is too long',
    }

Messages can be overridden on a global basis, using :attr:`validator_msgs` on the middleware configuration. For example, the user may prefer "Value is required" instead of the default "Enter a value" for a missing field.

A Validator can also rename mesages, by specifying a tuple in the :attr:`msgs` dict. For example, :class:`ListLengthValidator` is a subclass of :class:`LengthValidator` which raises either ``tooshort`` or ``toolong``. However, it's desired to have different message names, so that any global override would be applied separately. The following :attr:`msgs` dict is used::

    msgs = {
        'tooshort': ('list_tooshort', 'Select at least $min'),
        'toolong': ('list_toolong', 'Select no more than $max'),
    }

Within the messages, tags like ``$min`` are substituted with the corresponding attribute from the validator. It is not possible to specify the value in this way; this is to discourage using values within messages.

**FormEncode**

Earlier versions of ToscaWidgets used FormEncode for validation and there are good reasons for this. Some aspects of the design work very well, and FormEncode has a lot of clever validators, e.g. the ability to check that a post code is in the correct format for a number of different countries.

However, there are challenges making FormEncode and ToscaWidgets work together. For example, both libraries store the widget hierarchy internally. This makes implementing some features (e.g. ``strip_name`` and :class:`tw2.dynforms.HidingSingleSelectField`) difficult. There are different needs for the handling of unicode, leading ToscaWidgets to override some behaviour. Also, FormEncode just does not support client-side validation, a planned feature of ToscaWidgets 2.

ToscaWidgets 2 does not rely on FormEncode. However, developers can use FormEncode validators for individual fields. The API is compatible in that :meth:`to_python` and :meth:`from_python` are called for conversion, and :class:`formencode.Invalid` is caught. Also, if FormEncode is installed, the :class:`ValidationError` class is a subclass of :class:`formencode.Invalid`.


Using Validators
~~~~~~~~~~~~~~~~

There's two parts to using validators. First, specify validators in the widget definition, like this::

    class RegisterUser(twf.TableForm):
        validator = twc.MatchValidator('email', 'confirm_email')
        name = twf.TextField()
        email = twf.TextField(validator=twc.EmailValidator)
        confirm_email = twf.PasswordField()

You can specify a validator on any widget, either a class or an instance. Using an instance lets you pass parameters to the validator. You can code your own validator by subclassing :class:`tw2.core.Validator`. All validators have at least these parameters:

.. autoclass:: tw2.core.Validator

Second, when the form values are submitted, call :meth:`validate` on the outermost widget. Pass this a dictionary of the request parameters. It will call the same method on all contained widgets, and either return the validated data, with all conversions applied, or raise :class:`tw2.core.ValidationError`. In the case of a validation failure, it stores the invalid value and an error message on the affected widget.

**Chaining Validators**

In some cases you may want validation to succeed if any one of a number of
checks pass.  In other cases you may want validation to succeed only if the
input passes `all` of a number of checks.  For this, :mod:`tw2.core` provides
the :class:`Any` and :class:`All` validators which are subclasses of the
extendable :class:`CompoundValidator`.

Implementation
~~~~~~~~~~~~~~

A two-pass approach is used internally, although this is generally hidden from the developer. When :meth:`Widget.validate` is called it first calls:

.. autofunction:: tw2.core.validation.unflatten_params

If this fails, there is no attempt to determine which parameter failed; the whole submission is considered corrupt. If the root widget has an ``id``, this is stripped from the dictionary, e.g. ``{'myid': {'param':'value', ...}}`` is converted to ``{'param':'value', ...}``. A widget instance is created, and stored in request local storage. This allows compatibility with existing frameworks, e.g. the ``@validate`` decorator in TurboGears. There is a hook in :meth:`display` that detects the request local instance. After creating the instance, validate works recursively, using the :meth:`_validate`. 

.. automethod:: tw2.core.Widget._validate

.. automethod:: tw2.core.RepeatingWidget._validate

.. automethod:: tw2.core.CompoundWidget._validate

Both :meth:`_validate` and :meth:`validate_python` take an optional state argument. :class:`CompoundWidget` and :class:`RepeatingWidget` pass the partially built dict/list to their child widgets as state. This is useful for creating validators like :class:`MatchValidator` that reference sibling values. If one of the child widgets fails validation, the slot is filled with an :class:`Invalid` instance.


General Considerations
======================

**Request-Local Storage**

ToscaWidgets needs access to request-local storage. In particular, it's important that the middleware sees the request-local information that was set when a widget is instatiated, so that resources are collected correctly.

The function tw2.core.request_local returns a dictionary that is local to the current request. Multiple calls in the same request always return the same dictionary. The default implementation of request_local is a thread-local system, which the middleware clears before and after each request.

In some situations thread-local is not appropriate, e.g. twisted. In this case the application will need to monkey patch request_local to use appropriate request_local storage.

**pkg_resources**

tw2.core aims to take advantage of pkg_resources where it is available, but not to depend on it. This allows tw2.core to be used on Google App Engine. pkg_resources is used in two places:

 * In ResourcesApp, to serve resources from modules, which may be zipped eggs. If pkg_resources is not available, this uses a simpler system that does not support zipped eggs.
 * In EngingeManager, to load a templating engine from a text string, e.g. "genshi". If pkg_resources is not available, this uses a simple, built-in mapping that covers the most common template engines.

**Framework Interface**

ToscaWidgets is designed to be standalone WSGI middeware and not have any framework interactions. However, when using ToscaWidgets with a framework, there are some configuration settings that need to be consistent with the framework, for correct interaction. Future vesions of ToscaWidgets may include framework-specific hooks to automatically gather this configuration. The settings are:

 * default_view - the template engine used by the framework. When root widgets are rendered, they will return a type suitable for including in this template engine. This setting is not needed if only Page widgets are used as root widgets, as there is no containing template in that case.
 * translator - needed for ToscaWidget to use the same i18n function as the framework.

**Unit Tests**

To run the tests, in ``tw2.devtools/tests`` issue::

    nosetests --with-doctest --doctest-extension=.txt
