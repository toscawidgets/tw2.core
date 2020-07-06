.. _widgets:

Widgets
=======

Widgets are small self-contained components that can be reused
across the same web page or across multiple pages.

A widget typically has a state (its value) a configuration (its params)
a template that describes what should be displayed, one ore more
resources (javascript or CSS) needed during display and might have
some logic that has to be executed every time the widget is displayed.

Using Widgets
-------------

A typical widget will look like::

    class MyWidget(tw2.core.Widget):
        template = "mypackage.widgets.templates.mywidget"

Which will look for a template named ``mywidget.html``
into the ``templates`` python package within the ``widgets``
package of the ``mypackage`` application. The extension
expected for the file depends on the template engine used:

* mako: ``.mako``
* kajiki: ``.kajiki``
* jinja: ``.jinja``
* genshi: ``.genshi``

The template engine used to render the provided template
depends on the ``default_engine`` option provided when
configuring :class:`tw2.core.middleware.TwMiddleware`.

In case you don't want to save the template into a separate
file you can also set the ``inline_engine_name`` option
to one of the template engines and provide the template
as a string::

    class HelloWidgetTemplate(tw2.core.Widget):
        inline_engine_name = "kajiki"
        template = """
            <i>Hello <span py:for="i in range(1, 4)">${i}, </span></i>
        """

Displaying a widget is as simple as calling the :meth:`.Widget.display`::

    HelloWidgetTemplate.display()

Widget value
~~~~~~~~~~~~

Each Widget has a special paramter, which is ``value``. This parameter
contains the current state of the widget. Value will usually be
a single value or a dictionary containing multiple values 
(in case of :class:`tw2.core.widgets.CompoundWidget`).

You can use the value to drive what the widget should show once
displayed::

    class HelloWidgetValue(tw2.core.Widget):
        inline_engine_name = "kajiki"
        template = """
            <i>Hello ${w.value}</i>
        """

    >>> HelloWidgetValue.display(value='World')
    Markup('<i>Hello World</i>')

:class:`tw2.core.CompoundWidget` can contain multiple subwidgets
(children) and their value is typically a ``dict`` with values
for each one of the children::

    class CompoundHello(tw2.core.CompoundWidget):
        inline_engine_name = "kajiki"
        template = """
            <div py:for="c in w.children">
                ${c.display()}
            </div>
        """

        name = HelloWidgetValue()
        greeter = tw2.core.Widget(inline_engine_name="kajiki", 
                                  template="<span>From ${w.value}</span>")

    >>> CompoundHello(value=dict(name="Mario", greeter="Luigi")).display()
    Markup('<div><span>Hello Mario</span></div><div><span>From Luigi</span></div>')

Children of a compound widget (like :ref:`forms`) can be accessed
both as a list iterating over ``w.children`` or by name using
``w.children.childname``.

Parameters
~~~~~~~~~~

Widgets might require more information than just their value to display,
or might allow more complex kind of configurations. The options required
to configure the widget are provided through :class:`tw2.core.Param` objects
that define which options each widget supports.

If you want your widget to be configurable, you can make available one or more
options to your Widget and allow any user to set them as they wish::

    class HelloWidgetParam(tw2.core.Widget):
        inline_engine_name = "kajiki"
        template = """
            <i>Hello ${w.name}</i>
        """

        name = tw2.core.Param(description="Name of the greeted entity")

The parameters can be provided any time by changing configuration of
a widget::

    >>> w = HelloWidgetParam(name="Peach")
    >>> w.display()
    Markup('<i>Hello Peach</i>')
    >>> w2 = w(name="Toad")
    >>> w2.display()
    Markup('<i>Hello Toad</i>')

Or can be provided at ``display`` time itself::

    >>> HelloWidgetParam.display(name="Peach")
    Markup('<i>Hello Peach</i>')

Deferred Parameters
~~~~~~~~~~~~~~~~~~~

When a widget requires a parameter that is not available before
display time. That parameter can be set to a :class:`tw2.core.Deferred`
object.

Deferred objects will accept any callable and before the widget is displayed
the callable will be executed to fetch the actual value for the widget::

    >>> singleselect = SingleSelectField(options=tw2.core.Deferred(lambda: [1,2,3]))
    >>> singleselect.options
    <Deferred: <Deferred>>
    >>> singleselect.display()
    Markup('<select ><option value=""></option>\n <option value="1">1</option>\n <option value="2">2</option>\n <option value="3">3</option>\n</select>')

``Deferred`` is typically used when loading data from the content of a database
to ensure that the content is the one available at the time the widget is
displayed and not the one that was available when the application started::

    >>> userpicker = twf.SingleSelectField(
    ...     options=twc.Deferred(lambda: [(u.user_id, u.display_name) for u in model.DBSession.query(model.User)])
    ... )
    >>> userpicker.display()
    Markup('<select ><option value=""></option>\n <option value="1">Example manager</option>\n <option value="2">Example editor</option>\n</select>')

Builtin Widgets
~~~~~~~~~~~~~~~

The ``tw2.core`` packages comes with the basic buildin blocks needed
to create your own custom widgets.

.. automodule:: tw2.core.widgets
    :members:
    :member-order: bysource
    :exclude-members: WidgetMeta, WidgetBunch, DisplayOnlyWidgetMeta, default_content_type

.. autoclass:: tw2.core.Param
    :members:

.. autoclass:: tw2.core.Deferred
    :members:

.. _resources:

Resources
---------

ToscaWidgets comes with resources management for widgets too.

Some widgets might be complex enough that they need external
resources to work properly. Typically those are CSS stylesheets
or Javascript functions.

The need for those can be specified in the :attr:`.Widget.resources`
param, which is a list of resources the widget needs to work properly

The :class:`tw2.core.middleware.TwMiddleware` takes care of serving
all the resources needed by a widget through a :class:`tw2.core.resources.ResourcesApp`.
There is not need to setup such application manually, having a ``TwMiddleware``
in place will provide support for resources too.

When a widget is being prepared for display, all resources that it requires
(as specified by :attr:`tw2.core.Widget.resources`)
are registered into the current request and while the response page output
goes through the middleware it will be edited to add the links (or content) 
of those resources as specified by their location.

.. note::

    If a resource was already injected into the page during current request
    and another widget requires it, it won't be injected twice. ToscaWidgets
    is able to detect that it's the same resource (thanks to the resource ``id``)
    and only inject that once.

To add resources to a widget simply specify them in :attr:`tw2.core.Widget.resources`::

    class HelloWidgetClass(twc.Widget):
        inline_engine_name = "kajiki"
        template = """
            <i class="${w.css_class}">Hello ${w.name}</i>
        """

        name = twc.Param(description="Name of the greeted entity")
        css_class = twc.Param(description="Class used to display content", default="red")

        resources = [
            twc.CSSSource(src="""
                .red { color: red; }
                .green { color: green; }
                .blue { color: blue; }
            """)
        ]

Once the page where the widget is displayed is rendered, you will
see that it begins with::

    <!DOCTYPE html>
    <html>
    <head><style type="text/css">
                .red { color: red; }
                .green { color: green; }
                .blue { color: blue; }
            </style>
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta charset="utf-8">

Which contains the CSS resource you specified as a dependency of your widget.

In case you are using a solution to package your resources into bundles like
WebPack, WebAssets or similar, you might want to disable resources injection
using ``inject_resoures=False`` option provided to :class:`tw2.core.middleware.TwMiddleware`
to avoid injecting resources that were already packed into your bundle.


Builtin Resource Types
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: tw2.core.resources
    :members:
    :member-order: bysource
    :exclude-members: JSSymbol, ResourcesApp, prepare
    :no-inherited-members:
    