import pkg_resources as pk, sys, core
try:
    from dottedtemplatelookup import DottedTemplateLookup
    dotted_template_lookup = DottedTemplateLookup(input_encoding='utf-8', 
                                                       output_encoding='utf-8',
                                                       imports=[],
                                                       default_filters=[])
except ImportError:
    pass

class EngineError(core.WidgetError):
    "Errors inside ToscaWidgets, related to template engines."
    pass

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
            template_path = template
            engine_name = self._get_engine_name(template)
        
        if engine_name == 'genshi' and (template_path.startswith('/') or template_path[1] == ':'):
            engine_name = 'genshi_abs'


        if engine_name != 'cheetah':
            template = self[engine_name].load_template(template_path)

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
        orig_name = name
        if name == 'genshi_abs':
            name = 'genshi'
            options.update({'genshi.search_path': '/'})
        for entrypoint in pk.iter_entry_points("python.templating.engines"):
            print entrypoint
            if entrypoint.name == name:
                factory = entrypoint.load()
                break
        else:
            raise EngineError("No template engine available for '%s'" % name)

        if name == 'mako':
            if name not in self:
                self[name] = dotted_template_lookup
            return self[name]

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
