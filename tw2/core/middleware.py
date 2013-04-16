from __future__ import absolute_import

import types
import warnings
import webob as wo
from pkg_resources import iter_entry_points, DistributionNotFound
from paste.deploy.converters import asbool, asint

from . import core

import logging
import six
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
        (default: ['mako','genshi','jinja','kajiki'])

    `strict_engine_selection`
        If set to true, TW2 will only select rendering engines from within your
        preferred_rendering_engines, otherwise, it will try the default list if
        it does not find a template within your preferred list. (default: True)

    `rendering_engine_lookup`
        A dictionary of file extensions you expect to use for each type of
        template engine.
        (default: {
            'mako':['mak', 'mako'],
            'genshi':['genshi', 'html'],
            'jinja':['jinja', 'html'],
            'kajiki':['kajiki', 'html'],
        })

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
    preferred_rendering_engines = ['mako', 'genshi', 'jinja', 'kajiki']
    strict_engine_selection = True
    rendering_extension_lookup = {
        'mako': ['mak', 'mako'],
        'genshi': ['genshi', 'html'],
        'genshi_abs': ['genshi', 'html'], # just for backwards compatibility with tw2 2.0.0
        'jinja':['jinja', 'html'],
        'kajiki':['kajiki', 'html'],
        'chameleon': ['pt']
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

        # Here to avoid circular import
        from . import resources
        self._resources_module = resources

        self.app = app
        self.config = Config(**config)
        self.resources = resources.ResourcesApp(self.config)
        self.controllers = controllers or ControllersApp()

        rl = core.request_local()
        # Load up controllers that wanted to be registered before we were ready
        for widget, path in rl.get('queued_controllers', []):
            self.controllers.register(widget, path)

        rl['queued_controllers'] = []

        # Load up resources that wanted to be registered before we were ready
        for modname, filename, whole_dir in rl.get('queued_resources', []):
            self.resources.register(modname, filename, whole_dir)

        rl['queued_resources'] = []

        # Future resource registrations should know to just plug themselves into
        # me right away (instead of being queued).
        rl['middleware'] = self

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

            ct = resp.headers.get('Content-Type', 'text/plain').lower()

            should_inject = (
                self.config.inject_resources
                and 'html' in ct
                and not isinstance(resp.app_iter, types.GeneratorType)
            )
            if should_inject:
                body = self._resources_module.inject_resources(
                    resp.body.decode(resp.charset),
                ).encode(resp.charset)
                if isinstance(body, six.text_type):
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

    def controller_path(self, target_widget):
        """ Return the path against which a given widget is mounted or None if
        it is not registered.
        """

        for path, widget in six.iteritems(self._widgets):
            if target_widget == widget:
                return path

        return None

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


def register_resource(modname, filename, whole_dir):
    """ API function for registering resources *for serving*.

    This should not be confused with resource registration for *injection*.
    A resource must be registered for serving for it to be also registered for
    injection.

    If the middleware is available, the resource is directly registered with
    the ResourcesApp.

    If the middleware is not available, the resource is stored in the
    request_local dict.  When the middleware is later initialized, those
    waiting registrations are processed.
    """

    rl = core.request_local()
    mw = rl.get('middleware')
    if mw:
        mw.resources.register(modname, filename, whole_dir)
    else:
        rl['queued_resources'] = rl.get('queued_resources', []) + [
            (modname, filename, whole_dir)
        ]
        log.debug("No middleware in place.  Queued %r->%r(%r) registration." %
                  (modname, filename, whole_dir))


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
        log.debug("No middleware in place.  Queued %r->%r registration." %
                  (path, widget))


def make_middleware(app=None, config=None, **kw):
    config = (config or {}).copy()
    config.update(kw)
    app = TwMiddleware(app, **config)
    return app


def make_app(config=None, **kw):
    return make_middleware(app=None, config=config, **kw)
