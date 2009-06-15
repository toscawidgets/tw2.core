# Framework interfaces

class tg(object):
    @classmethod
    def start_extension():
        import cherrypy as cp

        if not cp.config.get('toscawidgets.on', False):
            return

        # TBD
        engines = view.EngineManager()
        engines.load_all(cp._extract_config(), stdvars)

        core.config.default_engine = cp.config.get('tg.defaultview')
        core.config.prefix = cp.config.get('toscawidgets.prefix', '/toscawidgets')
        core.config.translator = gettext

        # TBD
        host_framework.webpath = cherrypy.config.get('server.webpath', '')
        serve_files = cherrypy.config.get('toscawidgets.serve_files', 1)

        # TBD: stack middleware
