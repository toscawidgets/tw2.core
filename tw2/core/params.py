import core, itertools, copy


class ParameterError(core.WidgetError):
    "Errors related to parameters."

class _Required(object):
    """This class is used to mark a widget parameter as being required, by
    setting the default value to this."""
    def __repr__(self):
        return 'Required'
Required = _Required()

class _Auto(object):
    """
    Used to explicitly mark a parameter as being automatically generated.
    """
    def __repr__(self):
        return 'Auto'
Auto = _Auto()

class Deferred(object):
    """This class is used as a wrapper around a parameter value. It takes a
    callable, which will be called every time the widget is displayed, with
    the returned value giving the parameter value."""
    def __init__(self, fn):
        self.fn = fn

class _Default(object):
    pass
    def __repr__(self):
        return 'Default'
Default = _Default()

_param_seq = itertools.count(0)

class Param(object):
    """A parameter for a widget.

    `description`
        A string to describe the parameter. When overriding a parameter
        description, the string can include ``$$`` to insert the previous
        description.

    `default`
        The default value for the parameter. If no defalt is specified,
        the parameter is a required parameter. This can also be specified
        explicitly using tw.Required.

    `request_local`
        Can the parameter be overriden on a per-request basis? (default:
        True)

    `attribute`
        Should the parameter be automatically included as an attribute?
        (default: False)

    `view_name`
        The name used for the attribute. This is useful for attributes like
        *class* which are reserved names in Python. If this is None, the name
        is used. (default: None)

    The class takes care to record which arguments have been explictly
    specifed, even if to their default value. If a parameter from a base
    class is updated in a subclass, arguments that have been explicitly
    specified will override the base class.
    """

    child_param = False
    internal = False
    name = None
    defined_on = None
    view_name = None

    def __init__(self, description=Default, default=Default, request_local=Default, attribute=Default, view_name=Default):
        self._seq = _param_seq.next()

        self.description = None
        if description is not Default:
            self.description = description
        self.default = Required
        if default is not Default:
            self.default = default
        self.request_local = True
        if request_local is not Default:
            self.request_local = request_local
        self.attribute = False
        if attribute is not Default:
            self.attribute = attribute
        self.view_name = None
        if view_name is not Default:
            self.view_name = view_name

        self.specified = []
        for arg in ['description', 'default', 'request_local', 'attribute', 'view_name']:
            if locals()[arg] is not Default:
                self.specified.append(arg)

    def __repr__(self):
        return '%s: %s (default: %s, defined on: %s)' % (self.name, self.description, self.default, self.defined_on)


class Variable(Param):
    """A variable - a parameter that is passed from the widget to the template,
    but cannot be controlled by the user. These do not appear in the concise
    documentation for the widget.
    """
    internal = True
    def __init__(self, description=Default, **kw):
        kw.setdefault('default', None)
        super(Variable, self).__init__(description, **kw)
        self.specified.append('internal')


class ChildParam(Param):
    """A parameter that applies to children of this widget

    This is useful for situations such as a layout widget, which adds a
    :attr:`label` parameter to each of its children. When a Widget subclass is
    defined with a parent, the widget picks up the defaults for any child
    parameters from the parent.
    """
    child_param = True


class ChildVariable(Variable, ChildParam):
    """A variable that applies to children of this widget
    """
    pass


class ParamMeta(type):
    "Meta class the collects parameters."

    def __new__(meta, name, bases, dct):
        """Create a new `Widget` subclass. This detects `Param` instances
        defined declaratively, updates with information from the containing
        class, and stores the objects in `_params`."""

        params = {}
        for b in bases:
            if hasattr(b, '_params'):
                params.update(b._all_params)

        for pname, prm in dct.items():
            if isinstance(prm, Param):
                if pname in params:
                    newprm = prm
                    prm = copy.copy(params[pname])
                    for a in newprm.specified:
                        setattr(prm, a, getattr(newprm, a))
                else:
                    prm.name = pname
                    if prm.view_name is None:
                        prm.view_name = pname
                    prm.defined_on = name

                params[pname] = prm
                if not prm.child_param and prm.default is not Required:
                    dct[pname] = prm.default
                else:
                    del dct[pname]
            elif pname in params:
                params[pname] = copy.copy(params[pname])
                params[pname].default = prm
                if prm is Required and pname != 'validator':
                    del dct[pname]

        ins = type.__new__(meta, name, bases, dct)
        ins._all_params = params
        ins._params = dict((p.name, p) for p in params.values()
                                                    if not p.child_param)
        return ins


class Parametered(object):
    __metaclass__ = ParamMeta
