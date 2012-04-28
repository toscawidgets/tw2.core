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
}


@memoize
def get_engine_name(template_name, mw=None):
    global engine_name_cache

    if template_name in engine_name_cache:
        return engine_name_cache[template_name]

    if ':' in template_name:
        engine_name = template_name.split(':', 1)[0]
        engine_name_cache[template_name] = engine_name

    try:
        return engine_name_cache[template_name]
    except KeyError:
        pass

    try:
        if mw is None:
            rl = core.request_local()
            mw = rl['middleware']
        pref_rend_eng = mw.config.preferred_rendering_engines
    except (KeyError, AttributeError):
        pref_rend_eng = ['mako', 'genshi']

    # find the first file in the preffered engines available for templating
    for engine_name in pref_rend_eng:
        try:
            get_source(engine_name, template_name)
            engine_name_cache[template_name] = engine_name
            return engine_name
        except IOError:
            pass

    if not mw.config.strict_engine_selection:
        pref_rend_eng = ['mako', 'genshi']
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
    from_loc, location, filename = template.rsplit('.', 2)
    module = __import__(location, globals(), locals(), [from_loc])
    parent_dir = SEP.join(module.__file__.split(SEP)[:-1])

    for extension in rendering_extension_lookup[engine_name]:
        abs_filename = parent_dir + SEP + filename + '.' + extension
        if os.path.exists(abs_filename):
            return abs_filename

    raise IOError("Couldn't find source for %r" % template)


@memoize
def get_source(engine_name, template, inline=False):
    if inline:
        return template

    # Strip off the leading engine name from the template if it exists
    if any(map(template.lstrip().startswith, rendering_extension_lookup)):
        template = template.split(':', 1)[1]

    if SEP in template:
        filename = template
    else:
        filename = _get_dotted_filename(engine_name, template)

    with open(filename, 'r') as f:
        return f.read()


@memoize
def get_render_callable(engine_name, displays_on, src):
    """ Returns a function that takes a template source and kwargs. """

    # TODO -- handle displays_on or remove it

    if engine_name == 'mako':
        import mako.template
        tmpl = mako.template.Template(src)
        return lambda kwargs: literal(tmpl.render(**kwargs))
    elif engine_name in ('genshi', 'genshi_abs'):
        import genshi.template
        tmpl = genshi.template.MarkupTemplate(src)
        return lambda kwargs: literal(tmpl.generate(**kwargs))

    raise NotImplementedError("Unhandled engine")


def render(template_name, displays_on, kwargs, inline=False, mw=None):
    """ Highest level function, here for convenience.

    Makes use of *all* other functions in this module.
    """

    engine_name = get_engine_name(template_name, mw)
    source = get_source(engine_name, template_name, inline)
    callback = get_render_callable(engine_name, displays_on, source)
    return callback(kwargs)
