Tutorial
========

Installation
------------

First of all, you need Python - version 2.5, 2.6 or 2.7. The recommended way to install ToscaWidgets is using `pip <http://pip.openplans.org/>`_. Once you have pip itself installed, you should issue (with sudo if required)::

    pip install tw2.dynforms tw2.devtools tw2.sqla genshi elixir

This install the widget libraries and a number of dependencies. Once this is complete, try running the widget browser to check this worked. Issue::

    paster tw2.browser

And browse to ``http://localhost:8000/``, where you should be able to see the installed widgets.

If you have any problems during install, try asking on the `group <http://groups.google.com/group/toscawidgets-discuss/>`_.


Using ToscaWidgets
------------------

ToscaWidgets can be used with a web framework, such as Pylons or TurboGears, or it can be used standalone, with ToscaWidgets itself as the framework. There are separate tutorials depending on how you want to use the library:

.. toctree::
   :maxdepth: 1

   standalone
   turbogears

If you are using a different framework, try asking on the `group <http://groups.google.com/group/toscawidgets-discuss/>`_.


Next Steps
----------

This tutorial has demonstrated the basic concepts of ToscaWidgets 2. To further your knowledge, a good place to look is the widget browser. There is also comprehensive design documentation, which explains how the different parts of ToscaWidgets work.


Import Styles
-------------

The Python import statement is flexible and allows several styles to be used:

 * The tutorials have import lines like ``import tw2.forms``, which makes each use of an imported widget quite long-winded, e.g. ``tw2.forms.TextField``.
 * A common approach is to use ``from tw2.forms import TextField``, which makes each usage more concise - just ``TextField``. However, it's then necessary to add each widget that will be used to the import line.
 * It is possible to use ``from tw2.forms import *``. However, this is discouraged for several reasons, including that it makes it difficult for a reader of the code to tell where a widget has been imported from.
 * An alternative approach is to use ``import tw2.forms as twf``, with each use then being ``twf.TextField``.

It is possible to use ToscaWidgets 2 with any of these. However, the latter form is favored, and documentation beyond the introductory tutorials will generally use that style.
