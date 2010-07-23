.. index:

ToscaWidgets 2 Documentation
============================

.. warning::
    All the tw2 branches are currently (as of July 2010) experimental, alpha software.

ToscaWidgets aims to be a practical and useful widgets framework that helps people build interactive websites with compelling features, faster and easier. Widgets are re-usable web components that can include a template, server-side code and JavaScripts/CSS resources. The library aims to be: flexible, reliable, documented, performant, and as simple as possible. For changes since ToscaWidgets 0.9, see :doc:`history`.

You can see the available widgets in the `Widget Browser <http://toscawidgets.org:8000/>`_.

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
   design
   devtools
   history
   future


Online Resources
----------------

The discussion group is `ToscaWidgets-discuss <http://groups.google.com/group/toscawidgets-discuss/>`_.

The bug tracker is `here <http://bitbucket.org/paj/tw2core/issues?status=new&status=open>`_ - all ToscaWidgets 2 issues should go here, regardless of which component the issue exists in. However, ToscaWidgets 0.9 bugs must not go on this tracker.

The official ToscaWidgets 2 repositories are:

 * http://bitbucket.org/paj/tw2core/
 * http://bitbucket.org/paj/tw2devtools/
 * http://bitbucket.org/paj/tw2forms/
 * http://bitbucket.org/paj/tw2dynforms/
 * http://bitbucket.org/paj/tw2.sqla/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

