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

    `bufsize`
        Buffer size used by static resource server. (default: 4096)
    '''

    translator = lambda s: s
    default_engine = 'string'

    inject_resources = True
    serve_resources = True
    res_prefix = '/resources/'
    bufsize = 4*1024

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

    def __call__(self, environ, start_response):
        rl = core.request_local()
        rl.clear()
        rl['middleware'] = self
        req = wo.Request(environ)
        if self.config.serve_resources and req.path.startswith(self.config.res_prefix):
            return self.resources(environ, start_response)
        else:
            resp = req.get_response(self.app)
            content_type = resp.headers.get('Content-Type','text/plain').lower()
            if self.config.inject_resources and 'html' in content_type:
                resp.body = resources.inject_resources(resp.body, encoding=resp.charset)
        core.request_local().clear()
        return resp(environ, start_response)
