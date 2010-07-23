Potential tutorial for a simple WSGI application. This is probably not a common use case.


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
        wrs.make_server('', 8000, twc.make_middleware(app)).serve_forever()

When you look at this with a browser, it should be like this:
