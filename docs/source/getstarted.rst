Getting Started
===============

.. _middleware:

Enabling ToscaWidgets
---------------------

ToscaWidgets is designed to work within a web request life cycle,
so some of its features rely on the a current request object
to be able to work a keep track of the state of widgets or
resources for the whole duration of the request.

For this reason, to start using ToscaWidgets you need to
wrap your WSGI application in the :class:`tw2.core.middleware.TwMiddleware`,
which is also used to configure ToscaWidgets itself::

    def application(environ, start_response):
        response_headers = [('Content-type', 'text/plain')]
        start_response("200 OK", response_headers)
        return [b"Hello World!"]

    from tw2.core.middleware import TwMiddleware
    application = TwMiddleware(application)

    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()

You can also provide all options available
to configure ToscaWidgets 
(those listed in :class:`tw2.core.middleware.Config`)
to ``TwMiddleware`` as keyword arguments to
change ToscaWidgets configuration::

    from tw2.core.middleware import TwMiddleware
    application = TwMiddleware(application, debug=False)

.. note::

    Debug mode is enabled by default in ToscaWidgets,
    so make sure you provide ``debug=False`` on production
    to leverage templates caching and other speedups.

Now that the middleare is in place, you can easily
display any widget you want into your application::

    from tw2.forms import SingleSelectField

    def application(environ, start_response):
        widget = SingleSelectField(options=[1, 2, 3])
        output = widget.display()

        response_headers = [('Content-type', 'text/html')]
        start_response("200 OK", response_headers)
        return [b"<h1>Hello World!</h1>",
                b"<p>Pick one of the options</p>",
                output.encode('ascii')]

    from tw2.core.middleware import TwMiddleware
    application = TwMiddleware(application)

    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()

See :ref:`widgets` and :ref:`forms` to get started
creating widgets and forms.

.. autoclass:: tw2.core.middleware.TwMiddleware
    :members:

Configuration Options
---------------------

.. autoclass:: tw2.core.middleware.Config
    :members:

