.. index:

ToscaWidgets 2 Documentation
============================

ToscaWidgets aims to be a practical and useful widgets framework that helps people build interactive websites with compelling features, faster and easier. Widgets are re-usable web components that can include a template, server-side code and JavaScripts/CSS resources. The library aims to be: flexible, reliable, documented, performant, and as simple as possible. For changes since ToscaWidgets 0.9, see :doc:`history`.

You can see the available widgets in the `Widget Browser
<http://tw2-demos.threebean.org/>`_.

ToscaWidgets 2 library packages follow the same naming convention, for example:

 * `tw2.core <http://github.com/toscawidgets/tw2.core/>`_ -- Core functionality -- no
   end-usable widgets here.
 * `tw2.forms <http://github.com/toscawidgets/tw2.forms/>`_ -- Basic forms library
 * `tw2.dynforms <http://github.com/toscawidgets/tw2.dynforms/>`_ -- Dynamic forms
   -- client-side and Ajax
 * `tw2.sqla <http://github.com/toscawidgets/tw2.sqla/>`_ -- SQLAlchemy database
   interface, similar to Sprox and Rum
 * `tw2.yui <http://github.com/toscawidgets/tw2.yui/>`_ -- tw2 wrappers around
   Yahoo User Interface widgets
 * `tw2.jquery <http://github.com/toscawidgets/tw2.jquery>`_ -- tw2
   wrappers around jQuery core functionality.
 * `tw2.jqplugins.ui <http://github.com/ralphbean/tw2.jqplugins.ui>`_ -- tw2
   wrappers around jQuery-UI widgets.
 * `tw2.jit <http://github.com/ralphbean/tw2.jit>`_ -- tw2 wrappers around the
   Javascript Infovis Toolkit.
 * ... and `many more
   <http://pypi.python.org/pypi?%3Aaction=search&term=tw2.&submit=search>`_.

----

**Online Resources**

 * Live demos -- Pick and choose from available libraries from the `tw2 Widget
   Browser <http://tw2-demos.threebean.org/>`_.
 * Tutorials for doing --

   * Dynamic database-driven forms with :doc:`tw2 and Pyramid </pyramid>`.
   * Dynamic database-driven forms with :doc:`tw2 and TurboGears 2.1
     </turbogears>`.
   * Dynamic database-driven forms with :doc:`tw2 all by its standalone self
     </standalone>`.
   * Interactive relationship graphs with `tw2.jit and Pyramid
     <http://threebean.wordpress.com/2011/03/07/sqlaradialgraph-in-a-pyramid-app>`_.
   * Interactive relationship graphs with `tw2.jit and TurboGears 2.1
     <http://threebean.wordpress.com/2011/03/06/sqlalchemy-the-javascript-infovis-toolkit-jit>`_.
   * `Database-aware jqgrid, with jqplot and portlets in a TG2.1 app
     <http://threebean.wordpress.com/2011/04/30/tutorial-melting-your-face-off-with-tw2-and-turbogears2-1>`_.
   * `Bubble charts with tw2.protovis
     <http://threebean.wordpress.com/2010/10/24/python-wsgi-protovis-barcamproc-fall-2010/>`_.
 * Nightly run `test results <http://tw2-tests.threebean.org/>`_.
 * Email list:  `toscawidgets-discuss
   <http://groups.google.com/group/toscawidgets-discuss/>`_.
 * IRC channel: ``#toscawidgets`` on ``irc.freenode.net``
 * Bug tracker:  `Paj's bitbucket account
   <http://bitbucket.org/paj/tw2core/issues?status=new&status=open>`_.

   * (All ToscaWidgets 2 issues should go here, regardless of which
     component the issue exists in. However, ToscaWidgets 0.9 bugs
     must not go on this tracker.)

----

**Contents**

.. toctree::
   :maxdepth: 2

   tutorial
   design
   devtools
   history


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

