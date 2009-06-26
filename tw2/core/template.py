import pkg_resources as pk, sys, core

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
        engine_name, template_path = template.split(':', 1)
        adaptor_renderer = self._get_adaptor_renderer(engine_name, displays_on)
        if engine_name == 'genshi' and (template_path.startswith('/') or template_path[1] == ':'):
            engine_name = 'genshi_abs'
        template = (template_path if engine_name == 'cheetah'
            else self[engine_name].load_template(template_path))
        output = adaptor_renderer(template=template, info=dct)
        if isinstance(output, str):
            output = output.decode('utf-8')
        return output

    def _get_adaptor_renderer(self, src, dst):
        """Return a function that will that processes a template appropriately,
        given the source and destination engine names.
        """
        if src == dst and src in ('kid', 'genshi'):
            return self[src].transform
        elif src == 'kid' and dst == 'genshi':
            from genshi.input import ET
            return lambda **kw: ET(self[src].transform(**kw))
        elif dst == 'genshi':
            from genshi.input import HTML
            return lambda **kw: HTML(self[src].render(**kw))
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
            if entrypoint.name == name:
                factory = entrypoint.load()
                break
        else:
            raise EngineError("No template engine available for '%s'" % name)

        if name == 'mako':
            options = options.copy()
            # emulate Kid and Genshi's dotted-path notation lookup
            options.setdefault('mako.directories', []).extend(sys.path)
            # make sure mako produces utf-8 output so we can decode it and use
            # unicode internally
            options['mako.output_encoding'] = 'utf-8'

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
