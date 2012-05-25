import os
import core

from util import memoize

from webhelpers.html import literal

# Just shorthand
SEP = os.path.sep

engine_name_cache = {}

rendering_extension_lookup = {
    'mako': ['mak', 'mako'],
    'genshi': ['html'],
    'genshi_abs': ['html'],  # just for backwards compatibility with tw2 2.0.0
    'jinja': ['jinja', 'html'],
    'kajiki': ['kajiki', 'html'],
    'chameleon': ['pt'],
}


@memoize
def get_engine_name(template_name, mw=None):
    global engine_name_cache

    if template_name in engine_name_cache:
        return engine_name_cache[template_name]

    if ':' in template_name:
        engine_name = template_name.split(':', 1)[0]
        engine_name_cache[template_name] = engine_name
        return engine_name

    try:
        if mw is None:
            rl = core.request_local()
            mw = rl['middleware']
        pref_rend_eng = mw.config.preferred_rendering_engines
    except (KeyError, AttributeError):
        pref_rend_eng = ['mako', 'genshi', 'jinja', 'kajiki', 'chameleon']

    # find the first file in the preffered engines available for templating
    for engine_name in pref_rend_eng:
        try:
            get_source(engine_name, template_name)
            engine_name_cache[template_name] = engine_name
            return engine_name
        except IOError:
            pass

    if not mw.config.strict_engine_selection:
        pref_rend_eng = ['mako', 'genshi', 'jinja', 'kajiki', 'chameleon']
        for engine_name in pref_rend_eng:
            try:
                get_source(engine_name, template_name)
                engine_name_cache[template_name] = engine_name
                return engine_name
            except IOError:
                pass

    raise ValueError("Could not find engine name for %s" % template_name)


@memoize
def _get_dotted_filename(engine_name, template):
    template = _strip_engine_name(template)
    location, filename = template.rsplit('.', 1)
    module = __import__(location, globals(), locals(), ['*'])
    parent_dir = SEP.join(module.__file__.split(SEP)[:-1])

    for extension in rendering_extension_lookup[engine_name]:
        abs_filename = parent_dir + SEP + filename + '.' + extension
        if os.path.exists(abs_filename):
            return abs_filename

    raise IOError("Couldn't find source for %r" % template)

def _strip_engine_name(template):
    """ Strip off the leading engine name from the template if it exists. """
    if any(map(template.lstrip().startswith, rendering_extension_lookup)):
        return template.split(':', 1)[1]

    return template


@memoize
def get_source(engine_name, template, inline=False):
    if inline:
        return template

    if SEP in template:
        filename = _strip_engine_name(template)
    else:
        filename = _get_dotted_filename(engine_name, template)

    # TODO -- use a context manager here once we drop support for py2.5.
    f = open(filename, 'r')

    try:
        source = f.read()
    finally:
        f.close()

    return source


@memoize
def get_render_callable(engine_name, displays_on, src, filename=None):
    """ Returns a function that takes a template source and kwargs. """

    # See the discussion here re: `displays_on` -- http://bit.ly/JRqbRw

    if engine_name == 'mako':
        import mako.template
        args = dict(
            text=src,
            filename=filename,
        )

        if filename:
            from mako.lookup import TemplateLookup

            if SEP not in filename:
                filename = _get_dotted_filename(engine_name, filename)

            directory = os.path.sep.join(filename.split(os.path.sep)[:-1])
            args['lookup'] = TemplateLookup(directories=[directory])

        tmpl = mako.template.Template(**args)
        return lambda kwargs: literal(tmpl.render(**kwargs))
    elif engine_name in ('genshi', 'genshi_abs'):
        import genshi.template
        tmpl = genshi.template.MarkupTemplate(src)
        return lambda kwargs: literal(
            ''.join(tmpl.generate(**kwargs).serialize('xhtml'))
        )
    elif engine_name == 'jinja':
        import jinja2
        tmpl = jinja2.Template(src)
        return lambda kwargs: literal(tmpl.render(**kwargs))
    elif engine_name == 'kajiki':
        import kajiki
        tmpl = kajiki.XMLTemplate(src)
        return lambda kwargs: literal(tmpl(kwargs).render())
    elif engine_name == 'chameleon':
        import chameleon
        tmpl = chameleon.PageTemplate(src, filename=filename)
        return lambda kwargs: literal(tmpl.render(**kwargs).strip())

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
    source = get_source(engine_name, template_name, inline)

    # Establish the render function
    callback = get_render_callable(
        engine_name, displays_on, source, template_name)

    # Do it
    return callback(kwargs)
