import widgets as wd, util, core, params as pm
import threading, re, logging, wsgiref.util as wru, itertools, heapq, operator
import os, webob as wo, pkg_resources as pr, mimetypes, errno

log = logging.getLogger(__name__)


class Resource(wd.Widget):
    location = pm.Param('Location on the page where the resource should be placed. This can be one of: head, headbottom, bodytop or bodybottom.')
    id = None

class Link(wd.Widget):
    '''
    A link to a file.
    '''
    id = None
    link = pm.Param('Direct web link to file. If this is not specified, it is automatically generated, based on :attr:`modname` and :attr:`filename`.')
    modname = pm.Param('Name of Python module that contains the file.', default=None)
    filename = pm.Param('Path to file, relative to module base.', default=None)

    def prepare(self):
        super(Link, self).prepare()
        if not hasattr(self, 'link'):
            if not self.filename:
                raise pm.ParameterError("Either 'link' or 'filename' must be specified")
            resources = core.request_local()['middleware'].resources
            self.link = resources.register(self.modname, self.filename)

    def __hash__(self):
        return hash(hasattr(self, 'link') and self.link)
    def __eq__(self, other):
        return self.link == getattr(other, "link", None)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, getattr(self, 'link', '%s/%s'%(self.modname,self.filename)))

class JSLink(Link, Resource):
    '''
    A JavaScript source file.
    '''
    location = 'head'
    template = 'genshi:tw2.core.templates.jslink'

class CSSLink(Link, Resource):
    '''
    A CSS style sheet.
    '''
    media = pm.Param('Media tag', default='all')
    location = 'head'
    template = 'genshi:tw2.core.templates.csslink'

class JSSource(Resource):
    """
    Inline JavaScript source code.
    """
    src = pm.Param('Source code')
    location = 'bodybottom'
    template = 'genshi:tw2.core.templates.jssource'

    def __hash__(self):
        return hash(self.src)
    def __eq__(self, other):
        return self.src == getattr(other, "src", None)
    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.src)

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
        self.config = config

    def register(self, modname, filename):
        """Register a file for static serving, and return the web path.

        After this method has been called, for say ('tw2.forms',
        'static/forms.css'), the URL /resources/tw2.forms/static/forms.css will
        then serve that file from within the tw2.forms package. This works
        correctly for zipped eggs.

        *Security Consideration* - This file will be readable by users of the
        application, so make sure it contains no confidential data.

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
        modname = modname or ''
        path = modname + '/' + filename.strip('/')
        if path not in self._paths:
            ct, enc = mimetypes.guess_type(os.path.basename(filename))
            self._paths[path] = (modname, filename, ct, enc)
        return self.config.res_prefix + path

    def __call__(self, environ, start_response):
        req = wo.Request(environ)
        try:
            path = req.path_info[len(self.config.res_prefix):]
            if path not in self._paths:
                raise IOError()
            (modname, filename, ct, enc) = self._paths[path]
            if modname:
                stream = pr.resource_stream(modname, filename)
            else:
                stream = open(filename)
        except IOError:
            resp = wo.Response(status="404 Not Found")
        else:
            stream = wru.FileWrapper(stream, self.config.bufsize)
            resp = wo.Response(request=req, app_iter=stream, content_type=ct)
            if enc:
                resp.content_type_params['charset'] = enc
            expires = int(req.environ.get('toscawidgets.resources_expire', 0))
            resp.cache_expires(expires)
        return resp(environ, start_response)


class _ResourceInjector(util.MultipleReplacer):
    """ToscaWidgets can inject resources that have been registered for injection in
    the current request.

    Usually widgets register them when they're displayed and they have instances of
    :class:`tw.api.Resource` declared at their :attr:`tw.api.Widget.javascript` or
    :attr:`tw.api.Widget.css` attributes.

    Resources can also be registered manually from a controller or template by
    calling their :meth:`tw.api.Resource.inject` method.

    When a page including widgets is rendered, Resources that are registered for
    injection are collected in a request-local
    storage area (this means any thing stored here is only visible to one single
    thread of execution and that its contents are freed when the request is
    finished) where they can be rendered and injected in the resulting html.

    ToscaWidgets' middleware can take care of injecting them automatically (default)
    but they can also be injected explicitly, example::


       >>> from tw.api import JSLink, inject_resources
       >>> JSLink(link="http://example.com").inject()
       >>> html = "<html><head></head><body></body></html>"
       >>> inject_resources(html)
       '<html><head><script type="text/javascript" src="http://example.com"></script></head><body></body></html>'

    Once resources have been injected they are popped from request local and
    cannot be injected again (in the same request). This is useful in case
    :class:`injector_middleware` is stacked so it doesn't inject them again.

    Injecting them explicitly is neccesary if the response's body is being cached
    before the middleware has a chance to inject them because when the cached
    version is served no widgets are being rendered so they will not have a chance
    to register their resources.
    """

    def __init__(self):
        return util.MultipleReplacer.__init__(self, {
            r'<head.*?>': self._injector_for_location('head'),
            r'</head.*?>': self._injector_for_location('headbottom', False),
            r'<body.*?>': self._injector_for_location('bodytop'),
            r'</body.*?>': self._injector_for_location('bodybottom', False)
            }, re.I|re.M)

    def _injector_for_location(self, key, after=True):
        def inject(group, resources, encoding):
            for r in resources:
                r.prepare()
            inj = u'\n'.join([r.display(displays_on='string') for r in resources if r.location == key])
            inj = inj.encode(encoding)
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
            resources = core.request_local().pop('resources', None)
        if resources:
            encoding = encoding or find_charset(html) or 'utf-8'
            html = util.MultipleReplacer.__call__(self, html, resources, encoding)
        return html


# Bind __call__ directly so docstring is included in docs
inject_resources = _ResourceInjector().__call__


_charset_re = re.compile(r"charset\s*=\s*(?P<charset>[\w-]+)([^\>])*",
                         re.I|re.M)
def find_charset(string):
    m = _charset_re.search(string)
    if m:
        return m.group('charset').lower()
