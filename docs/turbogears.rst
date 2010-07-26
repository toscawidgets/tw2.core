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
    
To enable ToscaWidgets 2.0, edit ``middleware.py`` and add, just before the ``return app`` line::

    app = twc.make_middleware(app, default_engine='genshi')

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
