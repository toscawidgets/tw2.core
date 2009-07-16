.. index:

tw2.devtools
============

To keep tw2.core as minimal as possible, features needed only for development are in a separate package, tw2.devtools. The features in devtools are:

 * Widget browser
 * Widget library quick start


Widget Browser
--------------

The browser essentially enumerates the ``tw2.widgets`` entrypoint. When browsing a module, it iterates through the public names in the module, and displays any that is a Widget subclass. It also imports ``samples.py`` for demo widgets. This can contain :attr:`page_options` - a dict that gives attributes for the body tag in the containing page.

The parameters that are displayed are: all the required parameters, plus non-required parameters that are defined on anything other than the Widget base class. Variables are never shown.


Widget Library Quick Start
--------------------------

To create a widget library, issue::

    paster quickstart -t tw2.library tw2.mylib

This creates an empty template that gets you started.


Writing a good widget library
-----------------------------

`Widget browser`
    This is the main documentation for the library, and it needs to give a good introduction to a new user. Every widget should have a demo, and a clear description of the widget and parameters.

`Example application`
    There should be a simple example application that demonstrates the widgets in action. Ideally this should just be a single python file that works standalone.

`Parameters`
    Every widget should have a convenient set of parameters that allow common customisation with ease, and make more complex configuration possible.

`Validation`
    Every widget needs to work correctly with validation. When a form is submitted and there is a validation failure, all widgets should maintain the same appearance. This includes a widget with no value continuing to have no value.

`Growing`
    Every widget should work correctly within a tw2.dynforms Growing container.
