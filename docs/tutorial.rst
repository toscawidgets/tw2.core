Tutorial
========

This tutorial will show you how to get ToscaWidgets 2 working with a WSGI application. You need to install tw2.core, tw2.devtools and tw2.forms, from the Mercurial repositories::

    hg clone http://bitbucket.org/paj/tw2core/ tw2.core
    hg clone http://bitbucket.org/paj/tw2devtools/ tw2.devtools
    hg clone http://bitbucket.org/paj/tw2forms/ tw2.forms

You need to run ``python setup.py develop`` for each repository.

To check the install worked, we will try to run the widget browser. Issue ``paster tw2.browser`` then browse to http://localhost:8000/. You should see the widget browser, like this:

.. image:: tut0.png


Simple WSGI Application
-----------------------

We'll start by creating a simple WSGI application, using WebOB. Create ``myapp.py`` with the following::

    import webob as wo, wsgiref.simple_server as wrs, os

    def app(environ, start_response):
        req = wo.Request(environ)
        resp = wo.Response(request=req, content_type="text/html; charset=UTF8")
        resp.body = 'hello world'
        return resp(environ, start_response)

    if __name__ == "__main__":
        wrs.make_server('', 8000, app).serve_forever()

To check this works, run ``myapp.py``, and use a web browser to open ``http://localhost:8000/``. You should see ``hello world``.

.. note:: The finished files at the end of this tutorial are in the tw2.forms source repository, in the examples directory.


Using Widgets
-------------

We'll now add some widgets to the application. Update the code to this::

    import webob as wo, wsgiref.simple_server as wrs, os
    import tw2.core as twc, tw2.forms as twf

    class TestPage(twc.Page):
        title = 'ToscaWidgets Tutorial'
        class child(twf.TableForm):
            name = twf.TextField()
            group = twf.SingleSelectField(options=['', 'Red', 'Green', 'Blue'])
            notes = twf.TextArea()

    def app(environ, start_response):
        req = wo.Request(environ)
        resp = wo.Response(request=req, content_type="text/html; charset=UTF8")
        resp.body = TestPage.display().encode('utf-8')
        return resp(environ, start_response)

    if __name__ == "__main__":
        wrs.make_server('', 8000, twc.TwMiddleware(app)).serve_forever()

When you look at this with a browser, it should be like this:

.. image:: tut1.png


Creating Widgets
----------------

 * Decide what base class to use
 * Identify parameters
 * Write template
 * Add any ``prepare()`` code you need
