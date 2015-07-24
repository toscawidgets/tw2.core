import os
from . import core

from .util import memoize, relpath

from markupsafe import Markup
import six
from six.moves import map
from six.moves import zip

# Just shorthand
SEP, ALTSEP, EXTSEP = os.path.sep, os.path.altsep, os.path.extsep

engine_name_cache = {}

_default_rendering_extension_lookup = {
    'mako': ['mak', 'mako'],
    'genshi': ['genshi', 'html'],
    # just for backwards compatibility with tw2 2.0.0
    'genshi_abs': ['genshi', 'html'],
    'jinja': ['jinja', 'html'],
    'chameleon': ['pt']
}

if not six.PY3:
    _default_rendering_extension_lookup.update({
        'kajiki': ['kajiki', 'html'],
    })


def get_rendering_extensions_lookup(mw):
    if mw is None:
        rl = core.request_local()
        mw = rl.get('middleware')
        if mw is None:
            return _default_rendering_extension_lookup
    return mw.config.rendering_extension_lookup


@memoize
def get_engine_name(template_name, mw=None):
    if template_name in engine_name_cache:
        return engine_name_cache[template_name]

    if template_name and ':' in template_name:
        engine_name = template_name.split(':', 1)[0]
        engine_name_cache[template_name] = engine_name
        return engine_name

    try:
        if mw is None:
            rl = core.request_local()
            mw = rl['middleware']
        pref_rend_eng = mw.config.preferred_rendering_engines
    except (KeyError, AttributeError):
        pref_rend_eng = ['mako', 'genshi', 'jinja', 'chameleon']
        if not six.PY3:
            pref_rend_eng.append('kajiki')

    # find the first file in the preffered engines available for templating
    for engine_name in pref_rend_eng:
        try:
            get_source(engine_name, template_name, mw=mw)
            engine_name_cache[template_name] = engine_name
            return engine_name
        except IOError:
            pass

    if not mw.config.strict_engine_selection:
        pref_rend_eng = ['mako', 'genshi', 'jinja', 'chameleon']
        if not six.PY3:
            pref_rend_eng.append('kajiki')
        for engine_name in pref_rend_eng:
            try:
                get_source(engine_name, template_name, mw=mw)
                engine_name_cache[template_name] = engine_name
                return engine_name
            except IOError:
                pass

    raise ValueError("Could not find engine name for %s" % template_name)


@memoize
def _get_dotted_filename(engine_name, template, mw=None):
    rendering_extension_lookup = get_rendering_extensions_lookup(mw)
    template = _strip_engine_name(template, mw)
    location, filename = template.rsplit('.', 1)
    module = __import__(location, globals(), locals(), ['*'])
    parent_dir = SEP.join(module.__file__.split(SEP)[:-1])

    for extension in rendering_extension_lookup[engine_name]:
        abs_filename = parent_dir + SEP + filename + EXTSEP + extension
        if os.path.exists(abs_filename):
            return abs_filename

    raise IOError("Couldn't find source for %r" % template)


def _strip_engine_name(template, mw=None):
    """ Strip off the leading engine name from the template if it exists. """
    rendering_extension_lookup = get_rendering_extensions_lookup(mw)
    if any(map(template.lstrip().startswith, rendering_extension_lookup)):
        return template.split(':', 1)[1]

    return template


@memoize
def get_source(engine_name, template, inline=False, mw=None):
    if inline:
        return template

    if SEP in template or (ALTSEP and ALTSEP in template):
        filename = _strip_engine_name(template, mw=mw)
    else:
        filename = _get_dotted_filename(engine_name, template, mw=mw)

    # TODO -- use a context manager here once we drop support for py2.5.
    f = open(filename, 'r')

    try:
        source = f.read()
    finally:
        f.close()

    return source


@memoize
def get_render_callable(engine_name, displays_on, src, filename=None, inline=False):
    """ Returns a function that takes a template source and kwargs. """

    # See the discussion here re: `displays_on` -- http://bit.ly/JRqbRw

    directory = None
    if filename and not inline:
        if SEP not in filename and (not ALTSEP or ALTSEP not in filename):
            filename = _get_dotted_filename(engine_name, filename)

        directory = os.path.dirname(filename)

    if engine_name == 'mako':
        import mako.template
        args = dict(text=src, imports=["from markupsafe import escape_silent"],
                    default_filters=['escape_silent'])

        if directory:
            args['filename'] = relpath(filename, directory)
            from mako.lookup import TemplateLookup
            args['lookup'] = TemplateLookup(
                directories=[directory])

        tmpl = mako.template.Template(**args)
        return lambda kwargs: Markup(tmpl.render(**kwargs))

    elif engine_name in ('genshi', 'genshi_abs'):
        import genshi.template
        args = dict(
            source=src,
        )

        if directory:
            args['loader'] = genshi.template.TemplateLoader([
                genshi.template.loader.directory(directory),
            ])

        tmpl = genshi.template.MarkupTemplate(**args)
        return lambda kwargs: Markup(
            ''.join(tmpl.generate(**kwargs).serialize('xhtml'))
        )

    elif engine_name == 'jinja':
        import jinja2
        from .jinja_util import htmlbools
        env = jinja2.environment.Environment(autoescape=True)
        env.filters['htmlbools'] = htmlbools
        tmpl = env.from_string(src, template_class=jinja2.Template)
        tmpl.filename = filename
        return lambda kwargs: Markup(tmpl.render(**kwargs))

    elif engine_name == 'kajiki':
        import kajiki
        tmpl = kajiki.XMLTemplate(six.u(src), filename=filename)
        return lambda kwargs: Markup(tmpl(kwargs).render())

    elif engine_name == 'chameleon':
        import chameleon
        tmpl = chameleon.PageTemplate(src, filename=filename)
        return lambda kwargs: Markup(tmpl.render(**kwargs).strip())

    raise NotImplementedError("Unhandled engine")


def render(template_name, displays_on, kwargs, inline=False, mw=None):
    """ Highest level function, here for convenience.

    Makes use of *all* other functions in this module.
    """

    # Determine the engine name
    if not inline:
        engine_name = get_engine_name(template_name, mw)
    else:
        engine_name = inline

    # Load the template source
    source = get_source(engine_name, template_name, inline, mw)

    # Establish the render function
    callback = get_render_callable(
        engine_name, displays_on, source, template_name, inline)

    # Do it
    return callback(kwargs)
