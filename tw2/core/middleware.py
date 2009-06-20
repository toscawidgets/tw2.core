import webob as wo, core, resources, template

class Config(object):
    '''
    ToscaWidgets Configuration Set

    `translator`
        The translator function to use. (default: no-op)

    `default_engine`
        The main template engine in use by the application. Widgets with no
        parent will display correctly inside this template engine. Other
        engines may require passing displays_on to :meth:`Widget.display`.
        (default:string)

    `inject_resoures`
        Whether to inject resource links in output pages. (default: True)

    `serve_resources`
        Whether to serve static resources. (default: True)

    `res_prefix`
        The prefix under which static resources are served. This must start
        and end with a slash. (default: /resources/)

    `serve_controllers`
        Whether to serve controller methods on widgets. (default: True)

    `controller_prefix`
        The prefix under which controllers are served. This must start
        and end with a slash. (default: /controllers/)

    `bufsize`
        Buffer size used by static resource server. (default: 4096)

    `params_as_vars`
        Whether to present parameters as variables in widget templates. This
        is the behaviour from ToscaWidgets 0.9. (default: False)

    `debug`
        Whether the app is running in development or production mode.
    '''

    translator = lambda s: s
    default_engine = 'string'
    inject_resources = True
    serve_resources = True
    res_prefix = '/resources/'
    serve_controllers = True
    controller_prefix = '/controllers/'
    bufsize = 4*1024
    params_as_vars = False
    debug = False

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class TwMiddleware(object):
    """ToscaWidgets middleware

    This performs three tasks:
     * Clear request-local storage before and after each request. At the start
       of a request, a reference to the middleware instance is stored in
       request-local storage.
     * Proxy resource requests to ResourcesApp
     * Inject resources
    """
    def __init__(self, app, **config):
        self.app = app
        self.config = Config(**config)
        self.engines = template.EngineManager()
        self.resources = resources.ResourcesApp(self.config)
        self.controllers = ControllersApp(self.config)

    def __call__(self, environ, start_response):
        rl = core.request_local()
        rl.clear()
        rl['middleware'] = self
        req = wo.Request(environ)
        if self.config.serve_resources and req.path.startswith(self.config.res_prefix):
            return self.resources(environ, start_response)
        else:
            if self.config.serve_controllers and req.path.startswith(self.config.controller_prefix):
                resp = self.controllers(req)
            else:
                resp = req.get_response(self.app)
            content_type = resp.headers.get('Content-Type','text/plain').lower()
            if self.config.inject_resources and 'html' in content_type:
                resp.body = resources.inject_resources(resp.body, encoding=resp.charset)
        core.request_local().clear()
        return resp(environ, start_response)


class ControllersApp(object):
    """
    """

    def __init__(self, config):
        self._widgets = {}
        self.config = config

    def register(self, widget, path):
        self._widgets[path] = widget

    def __call__(self, req):
        try:
            path = req.path_info[len(self.config.controller_prefix):]
            resp = self._widgets[path].request(req)
        except KeyError:
            resp = wo.Response(status="404 Not Found")
        return resp
