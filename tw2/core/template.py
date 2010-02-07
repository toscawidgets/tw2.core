import pkg_resources as pk, sys, core,  os
import string

try:
    from tw2.core import mako_util
    from dottedtemplatelookup import DottedTemplateLookup
    dotted_template_lookup = DottedTemplateLookup(input_encoding='utf-8',
                                                       output_encoding='utf-8',
                                                       imports=[],
                                                       default_filters=[])
except ImportError:
    pass

class EngineError(core.WidgetError):
    "Errors inside ToscaWidgets, related to template engines."

rm = pk.ResourceManager()

def template_available(template_name, engine_name, mw=None):
    try:
        rendering_extension_lookup = mw.config.rendering_extension_lookup
    except (KeyError, AttributeError):
        rendering_extension_lookup = {'mako':'mak', 'genshi':'html', 'cheetah':'tmpl', 'kid':'kid'}

    ext = rendering_extension_lookup[engine_name]
    split = template_name.rsplit('.', 1)
    return os.path.isfile(rm.resource_filename(split[0], '.'.join((split[1], ext))))

engine_name_cache = {}

def reset_engine_name_cache():
    global engine_name_cache
    engine_name_cache = {}

def get_engine_name(template_name, mw=None):
    global engine_name_cache
    try:
        engine_name, template_path = template_name.split(':', 1)
        return engine_name
    except ValueError:
        pass
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
        pref_rend_eng = ['mako', 'genshi', 'cheetah', 'kid']
    #find the first file in the preffered engines that is available for templating
    for engine_name in pref_rend_eng:
        if template_available(template_name, engine_name, mw):
            engine_name_cache[template_name] = engine_name
            return engine_name
    if not mw.config.strict_engine_selection:
        pref_rend_eng = ['mako', 'genshi', 'cheetah', 'kid']
        for engine_name in pref_rend_eng:
            if template_available(template_name, engine_name):
                engine_name_cache[template_name] = engine_name
                return engine_name
    raise EngineError("Could not find template for: %s. You may need to specify \
a template engine name in the widget like mako:%s, or change the middleware setup \
to include the template's templating language in your preferred_template_engines \
configuration. As a last resort, you may set strict_template_selection to false \
which will grab whatever template it finds if there one of your preferred template \
engines is not found."""%(template_name, template_name))


class EngineManager(dict):
    """Manages template engines. An instance is automatically created on each
    :class:`tw.core.TwMiddleware` instance. Users should not access
    this class directly.
    """
    def render(self, template, displays_on, dct):
        """Render a template (passed in the form "engine_name:template_path")
        in a suitable way for inclusion in a template of the engine specified
        in ``displays_on``.
        """
        try:
            engine_name, template_path = template.split(':', 1)
        except ValueError:
            #if the engine name is not specified, find the best possible engine
            engine_name = get_engine_name(template)
            template_path = template
            

        if engine_name == 'genshi' and (template_path.startswith('/') or template_path[1] == ':'):
            engine_name = 'genshi_abs'

        if engine_name not in ['string', 'cheetah']:
            template = self[engine_name].load_template(template_path)

        if engine_name == 'string':
            template = template_path
            
        #xxx: add support for "toscawidgets" template engine
    
        adaptor_renderer = self._get_adaptor_renderer(engine_name, displays_on, template)

        if engine_name == 'mako':
            output = adaptor_renderer(**dct)
        else:
            output = adaptor_renderer(template=template_path, info=dct)
        if isinstance(output, str):
            output = output.decode('utf-8')
        return output

    def _get_adaptor_renderer(self, src, dst, template):
        """Return a function that will that processes a template appropriately,
        given the source and destination engine names.
        """
        if src =='string' or src=='toscawidgets':
            return lambda **kw: string.Template(template).substitute(**dict(kw['info']['w'].iteritems()))
        if src == dst and src in ('kid', 'genshi'):
            return self[src].transform
        elif src == 'mako' and dst == 'kid':
            from kid import XML
            return lambda **kw: XML(template.render(**kw))
        elif src=='mako' and dst=='genshi':
            from genshi.core import Markup
            return lambda **kw: Markup(template.render(**kw))
        elif src == 'mako':
            return template.render
        elif src == 'kid' and dst == 'genshi':
            from genshi.input import ET
            return lambda **kw: ET(self[src].transform(**kw))
        elif dst == 'genshi':
            from genshi.core import Markup
            return lambda **kw: Markup(self[src].render(**kw))
        elif dst == 'kid':
            from kid import XML
            return lambda **kw: XML(self[src].render(**kw))
        else:
            return self[src].render

    def load_engine(self, name, options={}, extra_vars_func=None):
        if name in self:
            raise EngineError("Template engine '%s' is already loaded" % name)
        if name == 'mako':
            self[name] = dotted_template_lookup
            return self[name]

        orig_name = name
        if name == 'genshi_abs':
            name = 'genshi'
            options.update({'genshi.search_path': '/'})

        try:
            factory = core.request_local()['middleware'].config.available_rendering_engines[name]
        except (KeyError, AttributeError):
            for entrypoint in pk.iter_entry_points("python.templating.engines"):
                if entrypoint.name == name:
                    factory = entrypoint.load()
                    break
            else:
                raise EngineError("No template engine available for '%s'" % name)

        self[orig_name] = factory(extra_vars_func, options)

    def __getitem__(self, name):
        """Return a Buffet plugin by name. If the plugin is not loaded it
        will try to load it with default arguments.
        """
        try:
            return dict.__getitem__(self, name)
        except KeyError:
            self.load_engine(name)
            return dict.__getitem__(self, name)

global_engines = EngineManager()
