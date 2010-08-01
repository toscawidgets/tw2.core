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
