import webob as wo, core, resources, template
from pkg_resources import iter_entry_points, DistributionNotFound

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

    `res_max_age`
        The maximum time a cache can hold the resource. This is used to
        generate a Cache-control header. (default: 3600)

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
        (default: True)

    `validator_msgs`
        A dictionary that maps validation message names to messages. This lets
        you override validation messages on a global basis. (default: {})

    `auto_reload_templates`
        Whether to automatically reload changed templates. Set this to False in
        production for efficiency. If this is None, it takes the same value as
        debug. (default: None)

    `preferred_rendering_engines`
        List of rendering engines in order of preference.
        (default: ['mako','genshi','kid','cheetah'])

    `strict_engine_selection`
        If set to true, TW2 will only select rendering engines from within your
        preferred_rendering_engines, otherwise, it will try the default list if
        it does not find a template within your preferred list. (default: True)

    `rendering_engine_lookup`
        A dictionary of file extensions you expect to use for each type of template engine.
        (default: {'mako':'mak', 'genshi':'html', 'cheetah':'tmpl', 'kid':'kid'})

    `script_name`
        A name to prepend to the url for all resource links (different from res_prefix, as it may
        Be shared across and entire wsgi app.
        (default: '')
    '''

    translator = lambda s: s
    default_engine = 'string'
    inject_resources = True
    serve_resources = True
    res_prefix = '/resources/'
    res_max_age = 3600
    serve_controllers = True
    controller_prefix = '/controllers/'
    bufsize = 4*1024
    params_as_vars = False
    debug = True
    validator_msgs = {}
    auto_reload_templates = None
    preferred_rendering_engines = ['mako', 'genshi', 'cheetah', 'kid']
    strict_engine_selection = True
    rendering_extension_lookup = {'mako':'mak', 'genshi':'html', 'cheetah':'tmpl', 'kid':'kid'}
    script_name = ''

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        if self.auto_reload_templates is None:
            self.auto_reload_templates = self.debug

        self.available_rendering_engines = {}
        for e in iter_entry_points("python.templating.engines"):
            if not self.strict_engine_selection or e.name in self.preferred_rendering_engines:
                try:
                    self.available_rendering_engines[e.name] = e.load()
                except DistributionNotFound:
                    pass

        #test to see if the rendering engines are available for the preferred engines selected
        for engine_name in self.preferred_rendering_engines:
            if engine_name not in self.available_rendering_engines:
                self.preferred_rendering_engines.remove(engine_name)


class TwMiddleware(object):
    """ToscaWidgets middleware

    This performs three tasks:
     * Clear request-local storage before and after each request. At the start
       of a request, a reference to the middleware instance is stored in
       request-local storage.
     * Proxy resource requests to ResourcesApp
     * Inject resources
    """
    def __init__(self, app, controllers=None, **config):
        self.app = app
        self.config = Config(**config)
        self.engines = template.EngineManager()
        self.resources = resources.ResourcesApp(self.config)
        self.controllers = controllers

    def __call__(self, environ, start_response):
        rl = core.request_local()
        rl.clear()
        rl['middleware'] = self
        req = wo.Request(environ)

        path = req.path_info
        if self.config.serve_resources and path.startswith(self.config.res_prefix):
            return self.resources(environ, start_response)
        else:
            if self.config.serve_controllers and path.startswith(self.config.controller_prefix):
                resp = self.controllers(req)
            else:
                if self.app:
                    resp = req.get_response(self.app)
                else:
                    resp = wo.Response(status="404 Not Found")
            content_type = resp.headers.get('Content-Type','text/plain').lower()
            if self.config.inject_resources and 'html' in content_type:
                body = resources.inject_resources(resp.body, encoding=resp.charset)
                if isinstance(body, unicode):
                    resp.unicode_body = body
                else:
                    resp.body = body
        core.request_local().clear()
        return resp(environ, start_response)


class ControllersApp(object):
    """
    """

    def __init__(self):
        self._widgets = {}

    def register(self, widget, path=None):
        if path is None:
            path = widget.id
        self._widgets[path] = widget

    def __call__(self, req):
        try:
            config = rl = core.request_local()['middleware'].config
            path = req.path_info.split('/')[1:]
            if path[0] != config.controller_prefix.strip('/'):
                return wo.Response(status="404 Not Found")
            widget_name = path[1] or 'index'
            widget = self._widgets[path[1]]
            resp = widget.request(req)
        except KeyError:
            resp = wo.Response(status="404 Not Found")
        return resp

global_controllers = ControllersApp()

def make_middleware(app=None, config=None, **kw):
    config = (config or {}).copy()
    config.update(kw)
    return TwMiddleware(app, controllers=global_controllers, **config)

def dev_server(app=None, host='127.0.0.1', port=8000, logging=True, weberror=True, **config):
    """
    Run a development server, hosting the ToscaWidgets application.
    This requires Paste and WebError, which are only sure to be available if
    tw2.devtools is installed.
    """
    config.setdefault('debug', True)
    config.setdefault('controller_prefix', '/')
    app = make_middleware(app, **config)

    if weberror:
        import weberror.errormiddleware as we
        app = we.ErrorMiddleware(app, debug=True)

    if logging:
        import paste.translogger as pt
        app = pt.TransLogger(app)

    import paste.httpserver as ph
    ph.serve(app, host=host, port=port)

# TBD: autoreload
