""" Collections of extra pieces to help smooth over community divergence. """

from widgets import Widget


class TGStyleController(Widget):
    """ A widget mixin that provides more advanced controller routing and
    dispatching.

    The need for this mainly sprung from a divergence of source trees
    (unintentionally forking) between the developers of tw2 while it was still
    alpha/beta.  One team expected users to define controllers as a 'request'
    classmethod on the widget and another team expected users to define a
    Controller class as a child of the widget.  Team A's pattern is now the
    default in the main tree.  This is a shim to support Team B's approach.

    Use it like this:

        >>> import tw2.core
        >>> class MyWidget(tw2.core.TGStyleController, tw2.core.Widget):
        ...     class Controller(object):
        ...         @jsonify
        ...         def some_method(self, req):
        ...             return dict(foo="bar")

    """

    @classmethod
    def dispatch(cls, req, controller):
        path = req.path_info.strip('/').split('/')[2:]
        if len(path) == 0:
            method_name = 'index'
        else:
            method_name = path[0]
        # later we want to better handle .ext conditions, but hey
        # this aint TG
        if method_name.endswith('.json'):
            method_name = method_name[:-5]
        method = getattr(controller, method_name, None)
        if not method:
            method = getattr(controller, 'default', None)
        return method

    @classmethod
    def request(cls, req):
        """
        Override this method to define your own way of handling a widget
        request.

        The default does TG-style object dispatch.
        """

        authn = cls.attrs.get('_check_authn')
        authz = cls.attrs.get('_check_authz')

        if authn and not authn(req):
            return util.abort(req, 401)

        controller = cls.attrs.get('controller', cls.Controller)
        if controller is None:
            return util.abort(req, 404)

        method = cls.dispatch(req, controller)
        if method:
            if authz and not authz(req, method):
                return util.abort(req, 403)

            controller = cls.Controller()
            return method(controller, req)
        return util.abort(req, 404)
