Javascript Integration
======================

ToscaWidget2 was designed to work with any Javascript framework
and integrate Python and Javascript as well as possible,
leading to a seamless development experience when you have
to provide Javascript callbacks or functions to your Python
declared widgets and forms.

Javascript on Display
---------------------

Frequently, when a widget is displayed, you might have to
run some form of initialization in JavaScript to attach
dynamic behaviours to it.

This can be done by using :meth:`tw2.core.Widget.add_call`
to register a `tw2.core.js.js_function` that should be
called.

A simple example might be to display a widget that shows
an "Hello World" alert every time it renders::

    import tw2.core as twc


    class HelloJSWidget(twc.Widget):
        message = twc.Param(description="Message to display")
        template = "<div></div>"
        inline_engine_name = "kajiki"

        def prepare(self):
            super(HelloJSWidget, self).prepare()

            alert = twc.js.js_function("alert")
            if self.message:
                self.add_call(alert(self.message))

As you can see we define a new :class:`tw2.core.js.js_function` named
"alert" and we assign it to the python "alert" variable.
If a message is provided, :meth:`tw2.core.Widget.add_call`
is used to register ``alert(self.message)`` as what should
be called every time the widget is rendered.

Displaying the widget in a web page::

    HelloJSWidget(message="Hello World").display()

will in fact open an alert box with the "Hello World" text.

But you are not constrained to use pre-existing Javascript
functions (like ``alert``), you can in fact declare your
own function (or use one that was imported from a :class:`tw2.core.resources.JSLink`).

For example we can change the previous widget to accept
only the name of the person to greet instead of the whole
message and display ``"Hello SOMEONE"`` always::

    class HelloJSWidget(twc.Widget):
        greeted = twc.Param(description="Who to greet")
        template = "<div></div>"
        inline_engine_name = "kajiki"

        def prepare(self):
            super(HelloJSWidget, self).prepare()
            sayhello = twc.js.js_function('(function(target){ alert("Hello " + target); })')

            if self.greeted:
                self.add_call(sayhello(self.greeted))

As you could see, instead of having out :class:`tw2.core.js.js_function` point
to an already existing one, we declared a new one that accepts
a ``target`` argument and displays an alert to greet the target.

The target of the greet message is then set in ``HelloJSWidget.prepare``
through the ``greeted`` param.

Displaying such widget will lead as expected to show an alert box
with "Hello" plus the name of the greeted person::

    HelloJSWidget(greeted="Mario").display()

It's also for example possible to run javascript that will target
the widget itself by using the :attr:`Widget.id` and :attr:`Widget.compound_id` 
properties to know the unique identifier of the widget in the dom.

Using such tactic we could rewrite the previous widget to always read
the greeted person from the content of the ``div`` instead of passing
it as an argument::

    class HelloJSWidget(twc.Widget):
        greeted = twc.Param(description="Who to greet")
        template = """<div id="$w.id">${w.greeted}</div>"""
        inline_engine_name = "kajiki"

        def prepare(self):
            super(HelloJSWidget, self).prepare()
            sayhello = twc.js.js_function('(function(widget_id){ var target = document.getElementById(widget_id).innerText; alert("Hello " + target); })')
            self.add_call(sayhello(self.id))

.. note::

    ``compound_id`` is safer to use, as it avoids collions
    when widgets with the same id are used within different
    parents. But is mostly only available in form fields. 
    On plain widgets you might need to use ``id`` itself.

Javascript Callbacks
--------------------

While being able to call javascript every time the widget is displayed
is essential to be able to attach advanced javascript behaviours to widgets,
sometimes you will need to trigger Javascript callbacks when something
happens on the widgets.

This can usually be done with :class:`tw2.core.js.js_callback` to declare the
javascript callback you care about.

A possible example is to run some javascript when the selected
option is changed in a single select field::

    alertpicker = twf.SingleSelectField(
        attrs={'onchange': twc.js.js_callback('alert("changed!")')},
        options=[(1, 'First'), (2, 'Second')]
    )

Builtin Javascript Helpers
--------------------------

.. automodule:: tw2.core.js
    :members:
    :no-inherited-members:
    