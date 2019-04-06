.. _forms:

Forms
=====

ToscaWidgets provides all the widgets related to
building HTML Forms in the ``tw2.forms`` package.

While ``tw2.core`` implements the foundation for
declaring any kind of widget, the ``tw2.forms``
is specialised in widgets that are needed to
create HTML forms.

Form
--------

A form is usually created by declaring a subclass
of a :class:`tw2.forms.Form`. Within the
form a ``child`` attribute that specifies the :ref:`formlayout`
(how the fields shoulb be arranged graphically)
through a subclass of :class:`tw2.forms.Layout` and then
within ``child`` all the fields of the form can be declared:

.. code-block:: python

    import tw2.core as twc
    import tw2.forms as twf


    class MovieForm(twf.Form):
        class child(twf.TableLayout):
            title = twf.TextField()
            director = twf.TextField(value='Default Director')
            genres = twf.SingleSelectField(options=['Action', 'Comedy', 'Romance', 'Sci-fi'])

        action = '/save_movie'

The form must also provide an ``action`` attribute
to specify where the form should be submitted.

.. note::

    If you are going to use ToscaWidgets with TurboGears
    you probably want the action to be a ``tg.lurl`` to
    ensure that prefix of your application is retained.

Form Buttons
~~~~~~~~~~~~

By default, each form comes with a **submit** button.

The submit button can be replaced by setting the
form ``submit`` attribute::

    class NameForm(twf.Form):
        class child(twf.TableLayout):
            name = twf.TextField()

        action = '/save_name'
        submit = twf.SubmitButton(value="Save Name")

Multiple buttons can also be provided for the form
by setting the ``buttons`` attribute::

    class NameForm(twf.Form):
        class child(twf.TableLayout):
            name = twf.TextField()

        action = '/save_name'
        buttons = [
            twf.SubmitButton(value="Save Name"),
            twf.ResetButton(),
            twf.Button(value="Say Hi", attrs=dict(onclick="alert('hi')"))
        ]

Dynamic Forms
~~~~~~~~~~~~~~~~

Children can be added and removed dynamically from forms
using the :meth:`.Widget.post_define` and :meth:`.Widget.prepare`
methods.

For example to change children of a form based on an option,
:meth:`.Widget.post_define` can be used::

    class GrowingMovieForm(twf.Form):
        class child(twf.TableLayout):
            @classmethod
            def post_define(cls):
                if not cls.parent:
                    return
                
                children = []

                for count in range(cls.parent.num_contacts):
                    class person_fieldset(twf.TableFieldSet):
                        id = "person_%s" % count
                        label = "Person #%s" % count
                        name = twf.TextField(validator=twc.Validator(required=True))
                        surname = twf.TextField()

                    children.append(person_fieldset(parent=cls))
        
                cls.children = children

        action = '/save_contacts'
        num_contacts = twc.Param(default=1)

    fivefieldsform = GrowingMovieForm(num_contacts=5)

.. note::

    Use the same ``fivefieldsform`` object for both display and
    validation. Trying to make a new ``GrowingMovieForm`` might not work
    even though ``num_contacts`` is always set to ``5``.

This will not work btw if you need to take action at display time.
In such case :meth:`Widget.prepare` is needed, for example to have
a text field that suggests the placeholder based on its original value::

    class DynamicText(twf.Form):
        class child(twf.TableLayout):
            text = twf.TextField(placeholder="Put text here")

        action = "/save_movie"    

        def prepare(self):
            super(DynamicText, self).prepare()

            if self.child.children.text.value:
                self.child.children.text.attrs = dict(
                    self.child.children.text.attrs,
                    placeholder="Put text here (was %s)" % self.child.children.text.value
                )

.. note::

    :meth:`Widget.prepare` is usually involved when setting a state that
    depends on the current request. For example current value of a field,
    or something else that is known only in current request. The resulting
    state of the widget is also only valid in current request, a different
    request might have nothing in common. Keep this in mind when using
    validation, as validation usually happens in a different request from
    the one that displayed the widget.

.. autoclass:: tw2.forms.widgets.Form
    :members:

Validating Forms
----------------

When you submit a form, it will send its data to the endpoint
you specified through the ``action`` parameter.

Before using it, you probably want to make sure that the
data that was sent is correct and display back to the user
error messages when it is not.

This can be done through :ref:`validation` and thanks to the
fact that Forms remember which form was just validated
in the current request.

For each field in the form it is possible to specify
a ``validator=`` parameter, which will be in charge of
validation for that field::

    class ValidatedForm(twf.Form):
        class child(twf.TableLayout):
            number = twf.TextField(placeholder="a number (1, 2, 3, 4)",
                                   validator=twc.validation.IntValidator())
            required = twf.TextField(validator=twc.Required)


To validate the data submitted through this form you can use
the :meth:`tw2.forms.widgets.Form.validate` method.

If the validation passes, the method will return the validated data::

    >>> ValidatedForm.validate({'numer': 5, 'required': 'hello'})
    {'numer': 5, 'required': 'hello'}

If the validation fails, it will raise a :class:`tw2.core.validation.ValidationError`
exception::

    Traceback (most recent call last):
        File "/home/amol/wrk/tw2.core/tw2/core/validation.py", line 106, in wrapper
            d = fn(self, *args, **kw)
        File "/home/amol/wrk/tw2.core/tw2/core/widgets.py", line 718, in _validate
            raise vd.ValidationError('childerror', exception_validator)
    tw2.core.validation.ValidationError

Such error can be trapped to get back the validated widget,
the value that was being validated and the error message for
each of its children::

    >>> try: 
    ...     ValidatedForm.validate({'numer': 'Hello', 'required': ''})
    ... except tw2.core.validation.ValidationError as e:
    ...     print(e.widget.child.value) 
    ...     for c in e.widget.child.children:
    ...         print(c.compound_key, ':', c.error_msg)

    {'numer': 'Hello', 'required': ''}
    numer : Must be an integer
    required : Enter a value

Also, trying to display back the form that was just validated, will
print out the error message for each field::

    >>> try: 
    ...     ValidatedForm.validate({'numer': 'Hello', 'required': ''})
    ... except tw2.core.validation.ValidationError as e:
    ...     print(e.widget.display())

    <form enctype="multipart/form-data" method="post">
        <span class="error"></span>
        
        <table>
        <tr class="odd error" id="numer:container">
            <th><label for="numer">Numer</label></th>
            <td>
                <input id="numer" name="numer" placeholder="a number (1, 2, 3, 4)" type="text" value="Hello"/>                
                <span id="numer:error">Must be an integer</span>
            </td>
        </tr><tr class="even required error" id="required:container">
            <th><label for="required">Required</label></th>
            <td>
                <input id="required" name="required" type="text" value=""/>
                <span id="required:error">Enter a value</span>
            </td>
        </tr>
        </table>
        <input type="submit" value="Save"/>
    </form>

For convenience, you can also recover the currently validated instance
of the form anywhere in the code. Even far away from the exception
that reported the validation error.

This can be helpful when you are isolating validation into a separate
Aspect of your application and then you need to recover the form instance
that includes the errors to display into your views.

To retrieve the currently validated widget, you can just use :meth:`tw2.core.widget.Widget.req`::

    >>> try: 
    ...     ValidatedForm.validate({'numer': 'Hello', 'required': ''})
    ... except tw2.core.validation.ValidationError as e:
    ...     print(e.widget)
    ...     print(ValidatedForm.req())
    
    <__main__.ValidatedForm object at 0x7f9432e5e080>
    <__main__.ValidatedForm object at 0x7f9432e5e080>

As you can see ``ValidatedForm.req()`` returns the same exact instance
that ``e.widget`` was. That's because when ``Widget.req()`` is used
and there is a validated instance of that same exact widget in the current
request, ToscaWidgets will assume you are trying to access the widget
you just validated and will return that one instace of building a 
new instance.

If you want a new instance, you can still do ``ValidatedForm().req()``
instead of ``ValidatedForm.req()``::


    >>> try: 
    ...     ValidatedForm.validate({'numer': 'Hello', 'required': ''})
    ... except tw2.core.validation.ValidationError as e:
    ...     print(e.widget)
    ...     print(ValidatedForm().req())

    <__main__.ValidatedForm object at 0x7f9432e5e080>
    <tw2.core.params.ValidatedForm_d object at 0x7f9432420940>

Keep in mind that this only keeps memory of the *last* widget
that failed validation. So in case multiple widgets failed validation
in the same request, you must used :attr:`tw2.core.validation.ValidationError.widget`
to access each one of them.

.. _formlayout:

Form Layout
---------------------

A layout specifies how the fields of the form
should be arranged.

This can be specified by having ``Form.child``
inherit from a specific layout class::

    class NameForm(twf.Form):
        class child(twf.TableLayout):
            name = twf.TextField()

or::

    class NameForm(twf.Form):
        class child(twf.ListLayout):
            name = twf.TextField()

Custom Layouts
~~~~~~~~~~~~~~

A custom layout class can also be made to
show the children however you want::

    class Bootstrap3Layout(twf.BaseLayout):
        inline_engine_name = "kajiki"
        template = """
    <div py:attrs="w.attrs">
        <div class="form-group" py:for="c in w.children_non_hidden" title="${w.hover_help and c.help_text or None}" py:attrs="c.container_attrs" id="${c.compound_id}:container">
            <label for="${c.id}" py:if="c.label">$c.label</label>
            ${c.display(attrs={"class": "form-control"})}
            <span id="${c.compound_id}:error" class="error help-block" py:content="c.error_msg"/>
        </div>
        <py:for each="c in w.children_hidden">${c.display()}</py:for>
        <div id="${w.compound_id}:error" py:content="w.error_msg"></div>
    </div>"""

    class BootstrapNameForm(twf.Form):
        class child(Bootstrap3Layout):
            name = twf.TextField()

        submit = twf.SubmitButton(css_class="btn btn-default")

Complex Layouts
~~~~~~~~~~~~~~~

In case of complex custom layouts, you can even
specify the layout case by case in the form itself
with each children in a specific position accessing
the children using ``w.children.child_name``::

    class OddNameForm(twf.Form):
        class child(twf.BaseLayout):
            inline_engine_name = "kajiki"
            template = """
            <div py:attrs="w.attrs">
                <div py:with="c=w.children.name">
                    ${c.display()}
                    <span id="${c.compound_id}:error" py:content="c.error_msg"/>
                </div>
                <div py:with="c=w.children.surname">
                    ${c.display()}
                    <span id="${c.compound_id}:error" py:content="c.error_msg"/>
                </div>

                <py:for each="ch in w.children_hidden">${ch.display()}</py:for>
                <div id="${w.compound_id}:error" py:content="w.error_msg"></div>
            </div>
            """

            name = twf.TextField()
            surname = twf.TextField()

.. autoclass:: tw2.forms.widgets.BaseLayout
    :members:

.. autoclass:: tw2.forms.widgets.ListLayout
    :members:

.. autoclass:: tw2.forms.widgets.TableLayout
    :members:

.. autoclass:: tw2.forms.widgets.GridLayout
    :members:

.. autoclass:: tw2.forms.widgets.RowLayout
    :members:

Bultin Form Fields
------------------

``tw2.forms`` package comes with a bunch of builtin
widgets that can help you build the most common kind
of forms.

.. automodule:: tw2.forms.widgets
    :members:
    :member-order: bysource
