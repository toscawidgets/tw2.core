from __future__ import absolute_import

import re
import logging
import itertools
import os
import webob as wo
import pkg_resources as pr
import mimetypes
import inspect
import warnings
import wsgiref.util

from .widgets import Widget
from .util import MultipleReplacer
import tw2.core.core
from .params import Param, Variable, ParameterError, Required
from .middleware import register_resource
from .js import encoder, js_symbol

from markupsafe import Markup
import six

log = logging.getLogger(__name__)


# TBD is there a better place to put this?
mimetypes.init()
mimetypes.types_map['.ico'] = 'image/x-icon'


class JSSymbol(js_symbol):
    """ Deprecated compatibility shim with old TW2 stuff.  Use js_symbol. """

    def __init__(self, *args, **kw):
        warnings.warn("JSSymbol is deprecated.  Please use js_symbol")

        if len(args) > 1:
            raise ValueError("JSSymbol must receive up to only one arg.")

        if len(args) == 1 and 'src' in kw:
            raise ValueError("JSSymbol must receive only one src arg.")

        if len(args) == 1:
            kw['src'] = args[0]

        super(JSSymbol, self).__init__(**kw)

        # Backwards compatibility for accessing the source.
        self.src = self._name


class ResourceBundle(Widget):
    """ Just a list of resources.

    Use it as follows:

        >>> jquery_ui = ResourceBundle(resources=[jquery_js, jquery_css])
        >>> jquery_ui.inject()

    """

    @classmethod
    def inject(cls):
        cls.req().prepare()

    def prepare(self):
        super(ResourceBundle, self).prepare()

        rl = tw2.core.core.request_local()
        rl_resources = rl.setdefault('resources', [])
        rl_location = rl['middleware'].config.inject_resources_location

        if self not in rl_resources:
            for r in self.resources:
                r.req().prepare()


class Resource(ResourceBundle):
    location = Param(
        'Location on the page where the resource should be placed.' \
        'This can be one of: head, headbottom, bodytop or bodybottom. '\
        'None means the resource will not be injected, which is still '\
        'useful, e.g. static images.', default=None)
    id = None
    template = None

    def prepare(self):
        super(Resource, self).prepare()

        rl = tw2.core.core.request_local()
        rl_resources = rl.setdefault('resources', [])
        rl_location = rl['middleware'].config.inject_resources_location

        if self not in rl_resources:
            if self.location is '__use_middleware':
                self.location = rl_location

            rl_resources.append(self)


class Link(Resource):
    '''
    A link to a file.
    '''
    id = None
    link = Param(
        'Direct web link to file. If this is not specified, it is ' +
        'automatically generated, based on :attr:`modname` and ' +
        ':attr:`filename`.',
    )
    modname = Param(
        'Name of Python module that contains the file.',
        default=None,
    )
    filename = Param(
        'Path to file, relative to module base.',
        default=None,
    )
    no_inject = Param(
        "Don't inject this link. (Default: False)",
        default=False,
    )
    whole_dir = Param(
        "Make the whole directory available.  (Default: False)",
        default=False,
    )

    @classmethod
    def guess_modname(cls):
        """ Try to guess my modname.

        If I wasn't supplied any modname, take a guess by stepping back up the
        frame stack until I find something not in tw2.core
        """

        try:
            frame, i = inspect.stack()[0][0], 0
            while frame.f_globals['__name__'].startswith('tw2.core'):
                frame, i = inspect.stack()[i][0], i + 1

            return frame.f_globals['__name__']
        except Exception:
            return None

    @classmethod
    def post_define(cls):

        if not cls.no_inject:
            if getattr(cls, 'filename', None) and \
               type(cls.filename) != property:

                if not cls.modname:
                    cls.modname = cls.guess_modname()

                register_resource(
                    cls.modname or '__anon__', cls.filename, cls.whole_dir
                )

    def prepare(self):
        rl = tw2.core.core.request_local()
        if not self.no_inject:
            if not hasattr(self, 'link'):
                # TBD shouldn't we test for this in __new__ ?
                if not self.filename:
                    raise ParameterError(
                        "Either 'link' or 'filename' must be specified"
                    )
                resources = rl['middleware'].resources
                self.link = resources.resource_path(
                    self.modname or '__anon__', self.filename
                )
            super(Link, self).prepare()

    def __hash__(self):
        return hash(
            hasattr(self, 'link') and \
            self.link or \
            ((self.modname or '') + self.filename)
        )

    def __eq__(self, other):
        return (isinstance(other, Link) and self.link == other.link
            and self.modname == other.modname
            and self.filename == other.filename)

    def __repr__(self):
        return "%s('%s')" % (
            self.__class__.__name__,
            getattr(self, 'link', '%s/%s' % (self.modname, self.filename))
        )


class DirLink(Link):
    ''' A whole directory as a resource.

    Unlike :class:`JSLink` and :class:`CSSLink`, this resource doesn't inject
    anything on the page.. but it does register all resources under the
    marked directory to be served by the middleware.

    This is useful if you have a css file that pulls in a number of other
    static resources like icons and images.
    '''
    link = Variable()
    filename = Required
    whole_dir = True

    def prepare(self):
        resources = tw2.core.core.request_local()['middleware'].resources
        self.link = resources.resource_path(
            self.modname,
            self.filename,
        )


class JSLink(Link):
    '''
    A JavaScript source file.
    '''
    location = '__use_middleware'
    template = 'tw2.core.templates.jslink'


class CSSLink(Link):
    '''
    A CSS style sheet.
    '''
    media = Param('Media tag', default='all')
    location = 'head'
    template = 'tw2.core.templates.csslink'


class JSSource(Resource):
    """
    Inline JavaScript source code.
    """
    src = Param('Source code', default=None)
    location = 'bodybottom'
    template = 'tw2.core.templates.jssource'

    def __eq__(self, other):
        return isinstance(other, JSSource) and self.src == other.src

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.src)

    def prepare(self):
        super(JSSource, self).prepare()
        if not self.src:
            raise ValueError("%r must be provided a 'src' attr" % self)
        self.src = Markup(self.src)


class CSSSource(Resource):
    """
    Inline Cascading Style-Sheet code.
    """
    src = Param('CSS code', default=None)
    location = 'head'
    template = 'tw2.core.templates.csssource'

    def __eq__(self, other):
        return isinstance(other, CSSSource) and self.src == other.src

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.src)

    def prepare(self):
        super(CSSSource, self).prepare()
        if not self.src:
            raise ValueError("%r must be provided a 'src' attr" % self)
        self.src = Markup(self.src)


class _JSFuncCall(JSSource):
    """
    Internal use inline JavaScript function call.

    Please use tw2.core.js_function(...) externally.
    """
    src = None
    function = Param('Function name', default=None)
    args = Param('Function arguments', default=None)
    location = 'bodybottom'  # TBD: afterwidget?

    def __str__(self):
        if not self.src:
            self.prepare()
        return self.src

    def prepare(self):
        if not self.src:
            args = ''
            if isinstance(self.args, dict):
                args = encoder.encode(self.args)
            elif self.args:
                args = ', '.join(encoder.encode(a) for a in self.args)

            self.src = '%s(%s)' % (self.function, args)
        super(_JSFuncCall, self).prepare()

    def __hash__(self):
        if self.args:
            if isinstance(self.args, dict):
                sargs = encoder.encode(self.args)
            else:
                sargs = ', '.join(encoder.encode(a) for a in self.args)
        else:
            sargs = None

        return hash((hasattr(self, 'src') and self.src or '') + (sargs or ''))

    def __eq__(self, other):
        return (getattr(self, 'src', None) == getattr(other, 'src', None)
                and getattr(self, 'args', None) == getattr(other, 'args', None)
                )


class ResourcesApp(object):
    """WSGI Middleware to serve static resources

    This handles URLs like this:
        /resources/tw2.forms/static/forms.css

    Where:
        resources       is the prefix
        tw2.forms       is a python package name
        static          is a directory inside the package
        forms.css       is the file to retrieve

    For this to work, the file must have been registered in advance,
    using :meth:`register`. There is a ResourcesApp instance for each
    TwMiddleware instance.
    """

    def __init__(self, config):
        self._paths = {}
        self._dirs = []
        self.config = config

    def register(self, modname, filename, whole_dir=False):
        """ Register a file for static serving.

        After this method has been called, for say ('tw2.forms',
        'static/forms.css'), the URL /resources/tw2.forms/static/forms.css will
        then serve that file from within the tw2.forms package. This works
        correctly for zipped eggs.

        *Security Consideration* - This file will be readable by users of the
        application, so make sure it contains no confidential data. For
        DirLink resources, the whole directory, and subdirectories will be
        readable.

        `modname`
            The python module that contains the file to publish. You can also
            pass a pkg_resources.Requirement instance to point to the root of
            an egg distribution.

        `filename`
            The path, relative to the base of the module, of the file to be
            published. If *modname* is None, it's an absolute path.
        """
        if isinstance(modname, pr.Requirement):
            modname = os.path.basename(pr.working_set.find(modname).location)

        path = modname + '/' + filename.lstrip('/')

        if whole_dir:
            if path not in self._dirs:
                self._dirs.append(path)
        else:
            if path not in self._paths:
                self._paths[path] = (modname, filename)

    def resource_path(self, modname, filename):
        """ Return a resource's web path. """

        if isinstance(modname, pr.Requirement):
            modname = os.path.basename(pr.working_set.find(modname).location)

        path = modname + '/' + filename.lstrip('/')
        return self.config.script_name + self.config.res_prefix + path

    def __call__(self, environ, start_response):
        req = wo.Request(environ)
        try:
            path = environ['PATH_INFO']
            path = path[len(self.config.res_prefix):]

            if path not in self._paths:
                if '..' in path:  # protect against directory traversal
                    raise IOError()
                for d in self._dirs:
                    if path.startswith(d.replace('\\', '/')):
                        break
                else:
                    raise IOError()
            modname, filename = path.lstrip('/').split('/', 1)
            ct, enc = mimetypes.guess_type(os.path.basename(filename))
            if modname and modname != '__anon__':
                stream = pr.resource_stream(modname, filename)
            else:
                stream = open(filename)
        except IOError:
            resp = wo.Response(status="404 Not Found")
        else:
            stream = wsgiref.util.FileWrapper(stream, self.config.bufsize)
            resp = wo.Response(app_iter=stream, content_type=ct)
            if enc:
                resp.content_type_params['charset'] = enc
        resp.cache_control = {'max-age': int(self.config.res_max_age)}
        return resp(environ, start_response)


class _ResourceInjector(MultipleReplacer):
    """
    ToscaWidgets can inject resources that have been registered for injection
    in the current request.

    Usually widgets register them when they're displayed and they have
    instances of :class:`tw2.core.resources.Resource` declared at their
    :attr:`tw2.core.Widget.javascript` or :attr:`tw2.core.Widget.css`
    attributes.

    Resources can also be registered manually from a controller or template by
    calling their :meth:`tw2.core.resources.Resource.inject` method.

    When a page including widgets is rendered, Resources that are registered
    for injection are collected in a request-local storage area (this means
    any thing stored here is only visible to one single thread of execution
    and that its contents are freed when the request is finished) where they
    can be rendered and injected in the resulting html.

    ToscaWidgets' middleware can take care of injecting them automatically
    (default) but they can also be injected explicitly, example::

       >>> from tw2.core.resources import JSLink, inject_resources
       >>> JSLink(link="http://example.com").inject()
       >>> html = "<html><head></head><body></body></html>"
       >>> inject_resources(html)
       '<html><head><script type="text/javascript"
        src="http://example.com"></script></head><body></body></html>'

    Once resources have been injected they are popped from request local and
    cannot be injected again (in the same request). This is useful in case
    :class:`injector_middleware` is stacked so it doesn't inject them again.

    Injecting them explicitly is necessary if the response's body is being
    cached before the middleware has a chance to inject them because when the
    cached version is served no widgets are being rendered so they will not
    have a chance to register their resources.
    """

    def __init__(self):
        return MultipleReplacer.__init__(self, {
            r'<head(?!er).*?>': self._injector_for_location('head'),
            r'</head(?!er).*?>': self._injector_for_location(
                'headbottom', False
            ),
            r'<body.*?>': self._injector_for_location('bodytop'),
            r'</body.*?>': self._injector_for_location('bodybottom', False)
        }, re.I | re.M)

    def _injector_for_location(self, key, after=True):
        def inject(group, resources, encoding):
            inj = six.u('\n').join([
                r.display(displays_on='string')
                for r in resources
                if r.location == key
            ])
            if after:
                return group + inj
            return  inj + group
        return inject

    def __call__(self, html, resources=None, encoding=None):
        """Injects resources, if any, into html string when called.

        .. note::
           Ignore the ``self`` parameter if seeing this as
           :func:`tw.core.resource_injector.inject_resources` docstring
           since it is an alias for an instance method of a private class.

        ``html`` must be a ``encoding`` encoded string. If ``encoding`` is not
        given it will be tried to be derived from a <meta>.

        """
        if resources is None:
            resources = tw2.core.core.request_local().get('resources', None)
        if resources:
            encoding = encoding or find_charset(html) or 'utf-8'
            html = MultipleReplacer.__call__(
                self, html, resources, encoding
            )
            tw2.core.core.request_local().pop('resources', None)
        return html


# Bind __call__ directly so docstring is included in docs
inject_resources = _ResourceInjector().__call__


_charset_re = re.compile(
    r"charset\s*=\s*(?P<charset>[\w-]+)([^\>])*", re.I | re.M)


def find_charset(string):
    m = _charset_re.search(string)
    if m:
        return m.group('charset').lower()
