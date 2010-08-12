What's New in ToscaWidgets 2?
=============================

ToscaWidgets 2 is a complete rewrite of ToscaWidgets. The primary motivation is to simplify the library, as the ToscaWidgets 1 code had become overly complex over time. The complexity made it difficult to write more complex widgets, such as tw.dynforms, and making changes to the library became a risky process. Where backwards compatibility can be readily maintained, this has been done. For example, the widgets in tw2.forms have almost identical names and parameters to tw.forms. However, in many cases it has been necessary to break backwards compatibility to produce a consistent and simple library.


Per-Request Widget Instances
----------------------------

A key feature for widgets is their dynamic capabilities, the ability to for a widget to adapt each time it is displayed. ToscaWidgets 2 creates a new instance of a widget every time it is used in a request. This allows widget and application code to update widget attributes in the natural, pythonic manner, without multiple threads interfering with each other. For example, you may want to customise a TableForm, so when it's "cost" field is over 100, the "insurance" field is made bold, to draw the user's attention. The code for this would be::

    def prepare(self):
        super(MyWidget, self).prepare()
        if self.c.cost.value > 100:
            self.c.insurance.css_class = 'bold'

In ToscaWidgets 1, widget instances are singletons that exist for the life of the application. For thread safety, it's vital that their attributes are not modified during a request. This means that all dynamic parameters must be passed around as dictionaries, resulting in highly-complex code that is prone to bugs. The equivalent code would be::

    def update_params(self, params):
        super(MyWidget, self).update_params(params)        
        if params['value_for']('cost') > 100:
            params.setdefault('child_args', {}).setdefault('insurance', {})['css_class'] = 'bold'


Simplified Form Definitions
---------------------------

ToscaWidgets 2 places great emphasis on making the application code that defines forms as simple as possible. It allows a natural, declarative style; defining a form is as easy as::

    class MovieForm(twf.TableForm):
        id = twf.HiddenField()
        title = twf.TextField()
        
For comparison, the equivalent code in ToscaWidgets 1 is::

    class MovieForm(twf.TableForm):
        class children(twc.WidgetsList):
            id = twf.HiddenField()
            title = twf.TextField()
    movie_form = MovieForm()


Widget Controller Methods
-------------------------

In ToscaWidgets 1, widgets are purely view components. However, ToscaWidgets 2 allows widgets to define controller methods, for example::

    class PeopleLookupField(twy.AjaxLookupField):
        @classmethod
        def request(cls, req):
            return twc.encode(db.People.query.like('%'+req.GET.get('search')+'%'))

This allows Ajax widgets to be self-contained, rather than having functionality separated between the widget and a controller class.

.. warning::
    You must include any required authorisation checks in the ``request`` method.


Built-in Validation
-------------------

ToscaWidgets 1 uses FormEncode for validation. FormEncode is a popular validation library and works well for many use cases. However, ToscaWidgets 1 has considerable internal complexity to ensure that it interfaces correctly with FormEncode. In the past, this has been the cause of some subtle bugs related to complex forms. It also makes it difficult to correctly support validation for some complex widgets, such as HidingContainerMixin in tw.dynforms.

ToscaWidgets 2 has a built-in validation framework, which avoids much of the validation complexity in ToscaWidgets 1. It does not have as many validators as FormEncode, covering just the more common use cases. However, it is still possible to use FormEncode validators for individual fields (although not Schema or ForEach validators). This change has enabled validation support for GrowingGrid in tw2.dynforms. It also paves the way for future development of client-side validation.


Declarative Parameter Definitions
---------------------------------

When you're creating your own widgets, you'll need to define parameters for the widgets, the variables that users of the widgets can set. You'll want to provide documentation, and default values. ToscaWidgets 2 makes this straightforward::

    class MyWidget(twc.Widget):
        do_title = twc.Param('Whether to include a title row in the table', default=True)

For comparison, the equivalent code in ToscaWidgets 1 is::

    class MyWidget(twc.Widget):
        params = {
            'do_title': 'Whether to include a title row in the table'
        }
        dotitle = True

The new approach used in ToscaWidgets 2 allows more metadata to be recorded about parameters, enabling new features, such as parameters that automatically become attributes.


Consistency in IDs and Names
----------------------------

ToscaWidgets 2 has changed how ``id`` and ``name`` parameters are generated. Just like ToscaWidgets 1, a widget's full ID is generated by combining it's ID with those of its ancestors. ToscaWidgets 1 uses underscores as the separator, which causes problems when applications use underscores in widget names. ToscaWidgets 2 uses colons as the separator, and forbids colons in widget names. In additions, a widget's full name is identical to its full id. These changes simplify the development of complex client-side widgets, such as GrowingGrid in tw2.dynforms.


Layouts Separated from Containers
---------------------------------

ToscaWidgets 2 clearly separates the concept of form layouts and form containers. ToscaWidgets 1 combines these, so there are widgets for TableForm, ListForm, TableFieldSet and ListFieldSet. ToscaWidgets 2 has widgets for Form and FieldSet, and also for TableLayout and ListLayout. This enables more flexibility in defining new containers and layouts, and this enables the new GridLayout widget. For comptability, TableForm remains, which transparently converts to a Form widget containing a TableLayout, as do the other widgets from ToscaWidgets 1. This change affects tw2.dynforms, which now has GrowingGridLayout, instead of GrowingTableFieldSet and GrowingTableForm.


Explicitly Deferred Parameters
------------------------------

Sometimes it is desirable for parameters to be dynamically evaluated every time a widget is displayed. ToscaWidgets 1 automatically calls any parameter that is a callable, for example::

    class MyWidget(twc.Widget):
        date = lambda: time.strftime('%d/%m/%Y')

However, in some cases parameters may be callables, but this behaviour is not desired. A common example is passing SQLAlchemy mapped classes to widgets. ToscaWidgets 2 only calls parameters that are explicitly marked as ``Deferred``::

    class MyWidget(twc.Widget):
        date = twc.Deferred(lambda: time.strftime('%d/%m/%Y'))


Variables in Widget Templates
-----------------------------

In ToscaWidgets 2, the widget instance is available in the template as ``$w``. Parameters must be accessed as ``$w.param``. ToscaWidgets 1 made all parameters directly accessible as ``$param``. The behaviour can be enabled in ToscaWidgets 2 by setting the *params_as_vars* config option.


ToscaWidgets as a Framework
---------------------------

ToscaWidgets 1 was always intended to be used with another web framework, primarily TurboGears and Pylons. ToscaWidgets 2 has gained features that allow it to be used as a framework in its own right. This is primarily the ``Page`` and ``FormPage`` widgets, which enable applications to be coded like this::

    import tw2.core as twc, tw2.forms as twc
    
    class Index(twf.FormPage):
        title = 'My app'
        class child(twf.TableForm):
            name = twf.TextField()
            email = twf.TextField(validator=twc.EmailValidator)
    
    twc.dev_server()


Minor Differences
-----------------

 * Framework interfaces are almost completely removed; ToscaWidgets is just a piece of WSGI middleware.
 * Widget constructions do not accept positional arguments, as doing so is considered bad practice when multiple inheritence is in use.
 * A widget does not automatically get the ``resources`` from its base class.
 * tw.api has been removed; just use tw2.core
 * The toscawidgets simple template engine has been removed.
 * Widget.__call__ is no longer an alias for display, as this causes problems for Cheetah.
 * CalendarDatePicker is moved from tw2.forms to tw2.dynforms

In tw2.dynforms:

 * WriteOnlyTextField is removed; tw2.forms PasswordField has similar functionality
 * AjaxLookupField is removed; there are better widgets like this in libraries like YUI
    

ToscaWidgets 1
--------------

Python web widgets were pioneered in TurboGears and many of the key ideas remain. Once the value of widgets was realised, a move was made to create a separate library, this is ToscaWidgets. The key differences are:

 * ToscaWidget is framework independent.
 * Multiple template engines are supported.
 * Resource links are injected by rewriting the page on output.
 * The forms library is separate from the core widget library.
 * The tw namespace exists for widget libraries to be located in.

ToscaWidgets had some success, but did not gain as much usage as hoped, in part due to a lack of documentation in the beginning. 
