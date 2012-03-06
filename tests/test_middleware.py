"""
filling in the missing gaps in test coverage
"""
from unittest import TestCase
from webob import Request, Response
import testapi


class TestMiddlewareConfig(TestCase):
    def testAutoReloadSetting(self):
        """
        auto_reload_templates should be the same as debug by default
        according to the docstring
        """
        from tw2.core.middleware import Config
        c = Config()
        self.assert_(c.auto_reload_templates == c.debug,
                     (c.auto_reload_templates, c.debug))


class TestMiddleware(TestCase):
    def setUp(self):
        testapi.setup()

    def testServeController(self):
        """
        should dispatch to fake controllers by default
        """
        fake_controller_app = Response("FAKE")

        def fake_controllers(request):
            return fake_controller_app

        from tw2.core.middleware import TwMiddleware
        mw = TwMiddleware(None, controllers=fake_controllers)
        self.assert_(mw.config.serve_controllers)
        self.assert_(mw.config.controller_prefix)
        res = Request.blank(\
            "%s/fake" % mw.config.controller_prefix).get_response(mw)
        self.assert_(res.status_int == 200)
        self.assert_(fake_controller_app.body == res.body)

    def testWithoutApp(self):
        """
        should return a 404
        """
        from tw2.core.middleware import TwMiddleware
        mw = TwMiddleware(None)
        res = Request.blank("/").get_response(mw)
        self.assert_(res.status_int == 404)

    def testInjectResourcesUnicode(self):
        """
        strictly for coverage, resource injection is supposed to set
        the unicode body if the result of the resource injection is
        unicode, so trying to figure out how to fake that
        """
        fake_app = Response(unicode_body=u"\xea",
                            charset="utf8",
                            content_type="text/html")

        from tw2.core.middleware import TwMiddleware
        from tw2.core import resources

        def mock_inject(*a, **kw):
            return fake_app.unicode_body

        real = resources.inject_resources
        resources.inject_resources = mock_inject
        try:
            mw = TwMiddleware(fake_app)
            self.assert_(mw.config.inject_resources == True)
            res = Request.blank("/").get_response(mw)
            self.assert_(res.status_int == 200)
            self.assert_(res.unicode_body == fake_app.unicode_body,
                         res.unicode_body)
        finally:
            resources.inject_resources = real

    def testControllerApp(self):
        """
        controllerapp should dispatch to an object having id, and a
        request method taking a webob request based on path_info of
        request.
        """
        from tw2.core.middleware import ControllersApp, TwMiddleware
        controller_response = Response("CONTROLLER")

        class WidgetMock(object):
            def __init__(self):
                self.id = "fake"

            def request(self, request):
                return controller_response

        mock = WidgetMock()
        mw = TwMiddleware(None, controller_prefix="goo")
        testapi.request(1, mw)
        ca = ControllersApp()

        ca.register(mock)
        res = ca(Request.blank("/%s/%s" % (mw.config.controller_prefix,
                                          mock.id)))
        self.assert_(res.status_int == 200, res.status_int)
        self.assert_(res.body == controller_response.body, res.body)

        res = ca(Request.blank("/%s/404" % mw.config.controller_prefix))
        self.assert_(res.status_int == 404, res.status_int)
        res = ca(Request.blank("%s/404" % mw.config.controller_prefix))
        self.assert_(res.status_int == 404, res.status_int)

    def testControllerApp(self):
        """
        controllerapp should dispatch to an object having id, and a
        request method taking a webob request based on path_info of
        request.
        """
        import tw2.core
        from tw2.core.middleware import register_controller, TwMiddleware
        controller_response = Response("CONTROLLER")

        class WidgetMock(tw2.core.Widget):
            def request(self, request):
                return controller_response

        mw = TwMiddleware(None)
        testapi.request(1, mw)
        register_controller(WidgetMock, 'foobar')
        print WidgetMock.mounted_path()
        self.assert_(WidgetMock.mounted_path() == 'foobar')

    def testMakeMiddelware(self):
        from tw2.core.middleware import make_middleware
        make_middleware(None)
        # mw = make_middleware(repoze_tm=True) # this requires pulling in a ridiculous amount of deps

    # def testDevServer(self):
    #     import threading
    #     import time

    #     class ServerThread(threading.Thread):
    #         def run(self):
    #             from tw2.core.middleware import dev_server
    #             dev_server(None)

    #     server_thread = ServerThread()
    #     server_thread.daemon = True
    #     server_thread.start()
    #     time.sleep(.25)
    #     try:
    #         server_thread.join(.25)
    #         raise KeyboardInterrupt
    #     except KeyboardInterrupt:
    #         pass
