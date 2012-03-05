import warnings
import webob as wo
from pkg_resources import iter_entry_points, DistributionNotFound
from paste.deploy.converters import asbool, asint

import core
import resources
import template

import logging
log = logging.getLogger(__name__)


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

    `inject_resources_location`
        A location where the resources should be injected. (default: head)

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

    `encoding`
        The encoding to decode when performing validation (default: utf-8)

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
        A dictionary of file extensions you expect to use for each type of
        template engine.
        (default: {'mako':'mak','genshi':'html','cheetah':'tmpl','kid':'kid'})

    `script_name`
        A name to prepend to the url for all resource links (different from
        res_prefix, as it may be shared across and entire wsgi app.
        (default: '')
    '''

    translator = lambda self, s: s
    default_engine = 'string'
    inject_resources_location = 'head'
    inject_resources = True
    serve_resources = True
    res_prefix = '/resources/'
    res_max_age = 3600
    serve_controllers = True
    controller_prefix = '/controllers/'
    bufsize = 4 * 1024
    params_as_vars = False
    debug = True
    validator_msgs = {}
    encoding = 'utf-8'
    auto_reload_templates = None
    preferred_rendering_engines = ['mako', 'genshi', 'cheetah', 'kid']
    strict_engine_selection = True
    rendering_extension_lookup = {
        'mako': 'mak',
        'genshi': 'html',
        'cheetah': 'tmpl',
        'kid': 'kid',
    }
    script_name = ''

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

        # Set boolean properties
        boolean_props = (
            'inject_resources',
            'serve_resources',
            'serve_controllers',
            'params_as_vars',
            'strict_engine_selection',
            'debug',
        )
        for prop in boolean_props:
            setattr(self, prop, asbool(getattr(self, prop)))

        # Set integer properties
        for prop in ('res_max_age', 'bufsize'):
            setattr(self, prop, asint(getattr(self, prop)))

        if self.auto_reload_templates is None:
            self.auto_reload_templates = self.debug

        self.available_rendering_engines = {}
        for e in iter_entry_points("python.templating.engines"):
            if not self.strict_engine_selection or \
               e.name in self.preferred_rendering_engines:
                try:
                    self.available_rendering_engines[e.name] = e.load()
                except DistributionNotFound:
                    pass

        # test to see if the rendering engines are available for the preferred
        # engines selected
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
        self.controllers = controllers or ControllersApp()

        rl = core.request_local()
        for widget, path in rl.get('queued_controllers', []):
            self.controllers.register(widget, path)

        rl['queued_controllers'] = []

    def __call__(self, environ, start_response):
        rl = core.request_local()
        rl.clear()
        rl['middleware'] = self
        req = wo.Request(environ)

        path = req.path_info
        if self.config.serve_resources and \
           path.startswith(self.config.res_prefix):
            return self.resources(environ, start_response)
        else:
            if self.config.serve_controllers and \
               path.startswith(self.config.controller_prefix):
                resp = self.controllers(req)
            else:
                if self.app:
                    resp = req.get_response(self.app, catch_exc_info=True)
                else:
                    resp = wo.Response(status="404 Not Found")

            ct = resp.headers.get('Content-Type', 'text/plain')
            content_type = ct.lower()

            if self.config.inject_resources and 'html' in content_type:
                body = resources.inject_resources(
                    resp.body,
                    encoding=resp.charset,
                )
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
        log.info("Registered controller %r->%r" % (path, widget))
        if path is None:
            path = widget.id
        self._widgets[path] = widget

    def __call__(self, req):
        config = rl = core.request_local()['middleware'].config
        path = req.path_info.split('/')[1:]
        pre = config.controller_prefix.strip('/')
        if pre and path[0] != pre:
            return wo.Response(status="404 Not Found")
        path = path[1] if pre else path[0]
        widget_name = path or 'index'
        try:
            widget = self._widgets[widget_name]
        except KeyError:
            resp = wo.Response(status="404 Not Found")
        else:
            resp = widget.request(req)
        return resp


def register_controller(widget, path):
    """ API function for registering widget controllers.

    If the middleware is available, the widget is directly registered with the
    ControllersApp.

    If the middleware is not available, the widget is stored in the
    request_local dict.  When the middleware is later initialized, those
    waiting registrations are processed.
    """

    rl = core.request_local()
    mw = rl.get('middleware')
    if mw:
        mw.controllers.register(widget, path)
    else:
        rl['queued_controllers'] = \
                rl.get('queued_controllers', []) + [(widget, path)]
        log.info("No middleware in place.  Queued %r->%r registration." %
                 (path, widget))


def make_middleware(app=None, config=None, **kw):
    config = (config or {}).copy()
    config.update(kw)
    app = TwMiddleware(app, **config)
    return app


def dev_server(*args, **kwargs):
    """
    Deprecated; use tw2.devtools.dev_server insteads.
    """
    import tw2.devtools
    warnings.warn(
        'tw2.core.dev_server is deprecated; ' +
        'Use tw2.devtools.dev_server instead.'
    )
    tw2.devtools.dev_server(*args, **kwargs)
