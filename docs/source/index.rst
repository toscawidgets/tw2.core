.. index:

ToscaWidgets2 Documentation
===========================

ToscaWidgets is a HTML Widgets generation and management library.

It allows to create reusable widgets to show in web pages and
manages the dependencies of the widgets like Javascript and CSS
that those widgets might need to properly display and behave

.. code-block:: python

  class HelloWidget(twc.Widget):
      inline_engine_name = "kajiki"
      template = """
          <i>Hello ${w.name}</i>
      """

      name = twc.Param(description="Name of the greeted entity")

Widgets can then be displayed within your web pages
to create reusable components or forms::

  >>> HelloWidget(name="World").display()
  <i>Hello World</i>

Widgets have support for:

* Templating based on Kajiki, Mako, Genshi and Jinja2
* Resources, to bring in Javascript and CSS dependencies they need.
* Parameters, to configure their behaviour.
* Validation, to ensure proper data was provided and show validation errors to users.
* Hooks, to drive their behaviour at runtime.

ToscaWidgets2 also provides a ``tw2.forms`` package with ready to use
widgets to display Forms with input validation.

Content
-------

.. toctree::
  :maxdepth: 3

  getstarted
  widget
  forms
  validation
  javascript
  design
  changelog

Online Resources
----------------

ToscaWidgets, as it was originall born from TurboGears Widgets,
shares many online resources with TurboGears. If you have questions
on how to use TW2 feel free to ask them in TurboGears channel or Mailing List.

 * Bug tracker:  `GitHub <https://github.com/toscawidgets/tw2.core/issues>`_.
 * Gitter Channel: `TurboGears Channel <https://gitter.im/turbogears/Lobby>`_
 * Mailing List: `TurboGears Users <http://groups.google.com/group/turbogears>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

