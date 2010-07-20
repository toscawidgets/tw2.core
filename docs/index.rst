.. index:

ToscaWidgets 2 Documentation
============================

.. warning::
    All the tw2 branches are currently (as of July 2010) experimental, alpha software.

ToscaWidgets aims to be a practical and useful widgets framework that helps people build interactive websites with compelling features, faster and easier. Widgets are re-usable web components that can include a template, server-side code and JavaScripts/CSS resources. The library aims to be: flexible, reliable, documented, performant, and as simple as possible. For changes since ToscaWidgets 0.9, see :doc:`history`.

ToscaWidgets comes in two main packages:

 * tw2.core - the core functionality needed to use widgets in an app
 * tw2.devtools - widget browser, library template, (and resource collator, not yet implemented)

The idea is that only tw2.core needs to be installed on a server. It has minimal dependencies, while tw2.devtools has more, e.g. sphinx.

In addition, widget library packages follow the same naming convention, for example:

 * tw2.forms - Basic forms library
 * tw2.dynforms - Dynamic forms - client-side and Ajax
 * tw2.yui - TW wrappers around Yahoo User Interface widgets


Contents:

.. toctree::
   :maxdepth: 2

   tutorial
   standalone
   design
   devtools
   history
   future


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

