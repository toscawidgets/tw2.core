TurboGears 2
============

Enabling ToscaWidgets
---------------------

First, you need to create a TurboGears project. The full instructions are in the `TurboGears documentation <http://www.turbogears.org/2.0/docs/main/QuickStart.html>`_, briefly::

    paster quickstart
    
    Enter project name: myapp
    Enter package name [myapp]: myapp
    Do you need authentication and authorization in this project? [yes] no
    ...
    
    cd myapp
    python setup.py develop

There are two different sets of steps to enable ToscaWidgets 2.0 in different versions of TurboGears.  If you don't know what version of TurboGears you have installed, fire up a python interpreter and type::

    >>> import tg
    >>> tg.__version__
    '2.1b2'

If you're using TurboGears 2.1, edit ``myapp/config/app_cfg.py`` and add at the end::

    base_config.use_toscawidgets2 = True

If you're using TurboGears 2.0, instead edit ``myapp/config/middleware.py``, add ``import tw2.core as twc`` to the top of the file, and replace the line::

    app = make_base_app(global_conf, full_stack=True, **app_conf) 

with the following two lines::

      custom = lambda app : twc.make_middleware(app, default_engine='genshi') 
      app = make_base_app(global_conf, wrap_app=custom, full_stack=True, **app_conf) 

For -both- TurboGears versions 2.0 and 2.1, you will need to also remove a single spurious reference to ToscaWidgets 1.0.  Edit ``myapp/lib/base.py`` and remove the line::

    from tw.api import WidgetBunch

To check this worked::

    paster serve development.ini


Building a Form
---------------

**TBD**


Connecting to a Database
------------------------

**TBD**


Deployment to Production
------------------------

By default, TurboGears 2 has ToscaWidgets 0.9 enabled. The two libraries can co-exist, but for production sites it is recommended to only run one, for efficiency.

To disable ToscaWidgets 0.9, edit ``app_cfg.py`` and add at the end::

    base_config.use_toscawidgets = False
    
This prevents Catwalk from working, so in ``root.py`` comment out the following lines::

    #from catwalk.tg2 import Catwalk
    
    #admin = Catwalk(model, DBSession)
