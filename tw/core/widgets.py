import copy, weakref, re, itertools
import template, core, util, validation as vd, params as pm

_widget_seq = itertools.count(0)

class WidgetMeta(pm.ParamMeta):
    def __new__(meta, name, bases, dct):
        widget = super(WidgetMeta, meta).__new__(meta, name, bases, dct)
        widget._seq = _widget_seq.next()
        widget.post_define()
        return widget


class BaseWidget(pm.Parametered):
    """
    Base class for all widgets.

    This just sets up __new__, post_ etc.
    """
    __metaclass__ = WidgetMeta

    @classmethod
    def req(cls, **kw):
        ins = object.__new__(cls)
        ins.__init__(**kw)
        return ins

    def __new__(cls, **kw):
        return type(cls.__name__+'_s', (cls,), kw)

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @classmethod
    def post_define(cls):
        """
        This is a class method, that is called when a subclass of this Widget
        is created. Process static configuration here. Use it like this::

            class MyWidget(LeafWidget):
                @classmethod
                def post_define(cls):
                    super(MyWidget, cls).post_define() !!! TBD
                    id = getattr(cls,  'id', None)
                    if id and not id.startswith('my'):
                        raise pm.ParameterError("id must start with 'my'")

        post_define should always cope with missing data - the class may be an
        abstract class.
        """
        pass

    def prepare(self):
        """
        This is an instance method, that is called just before the Widget is
        displayed. Process request-local configuration here. For
        efficiency, widgets should do as little work as possible here.
        Use it like this::

            class MyWidget(LeafWidget):
                def prepare(self):
                    super(MyWidget, self).prepare()
                    self.value = 'My: ' + str(self.value)
        """
        pass


class Widget(BaseWidget):
    """
    Practical widget:

This is the base class for all widgets. Widgets have the following lifecycle:

 * A Widget subclass will be defined at application startup, with static configuration, e.g. id.
 * In each request, a Widget instance is created, with request-local configuration, e.g. value.

TBD: change this to explaining HOW you use a widget...

    Basic params for all widgets
    """

    id = pm.Param('Widget identifier', request_local=False)
    template = pm.Param('Template file for the widget, in the format engine_name:template_path.')
    validator = pm.Param('Validator for the widget.', default=vd.Validator(), request_local=False)
    attrs = pm.Param("Extra attributes to include in the widget's outer-most HTML tag.", default={})
    value = pm.Param("The value for the widget.", default=None)
    resources = pm.Param("Resources used by the widget. This must be an iterable, each item of which is a :class:`Resource` subclass.", default=[], request_local=False)

    error_msg = pm.Variable("Validation error message.")
    parent = pm.Variable("The parent of this widget, or None if this is a root widget.")

    _sub_compound = False
    id_elem = None
    _valid_id_re = re.compile(r'^[a-zA-Z][\w\-\_\.]*$')

    @classmethod
    def post_define(cls, cls2=None):
        """
        Define the widget:
          * Set attrs['id'] to the compound id
          * Get any defaults from the parent
        """
        cls = cls2 or cls
        id = getattr(cls, 'id', None)
        if id:
            if not cls._valid_id_re.match(id):
                raise pm.ParameterError("Not a valid identifier: '%s'" % id)
            if not cls.id_elem:
                cls.id_elem = id
            cls.attrs = cls.attrs.copy()
            cls.attrs['id'] = cls._compound_id()

        if cls.validator and not isinstance(cls.validator, vd.Validator):
            # TBD: do formencode as well or just hasattr to_python, from_python
            raise pm.ParameterError("Validator must be a tw.core.Validator instance, or a F")

        cls._deferred = [a for a in dir(cls) if isinstance(getattr(cls, a), pm.Deferred)]
        cls._attr = [p.name for p in cls._params.values() if p.attribute]

        if cls.parent:
            for p in cls.parent._all_params.values():
                if p.child_param and not hasattr(cls, p.name) and p.default is not pm.Required:
                    setattr(cls, p.name, p.default)


    def prepare(self):
        """
        Prepare the widget for display:
          * Call any deferred parameters
          * Place any attribute parameters in the ``attrs`` dict
          * Initialise and register any resources
          * Call ``validator.from_python`` on the value
        """
        if 0: # TBD debug mode only
            for k in kw:
                if not self._params[k].request_local:
                    raise pm.ParameterError("Cannot set non-request-local parameter '%s' in a request" % k)
            for p in self._params:
                if not hasattr(self, p):
                    raise pm.ParameterError("Missing required parameter '%s'" % p)

        for a in self._deferred:
            setattr(self, a, getattr(self, a).fn())
        if self._attr or 'attrs' in self.__dict__:
            self.attrs = self.attrs.copy()
            if self.id:
                self.attrs['id'] = self._compound_id()
            for a in self._attr:
                if a in self.attrs:
                    raise pm.ParameterError("Class with user-supplied attribute: '%s'" % a)
                self.attrs[a] = getattr(self, a)
        if self.validator: # TBD: and not self._validated:
            self.value = self.validator.from_python(self.value)
        if self.resources:
            core.request_local().setdefault('resources', set()).update(r for r in self.resources)

    @classmethod
    def _compound_id(cls):
        ancestors = []
        cur = cls
        while cur:
            ancestors.append(cur.id_elem)
            cur = cur.parent
        return ':'.join(reversed(filter(None, ancestors)))

    def display(self, displays_on=None):
        """Display the widget - render the template. In the template, the
        widget instance is available as the variable ``$w``.

        `displays_on`
            The name of the template engine this widget is being displayed
            inside. If not specified, this is determined automatically, from
            the parent's template engine, or the default, if there is no
            parent. Set this to ``string`` to get raw string output.
        """
        self.prepare()
        mw = core.request_local().get('middleware')
        if displays_on is None:
            displays_on = (self.parent.template.split(':')[0] if self.parent
                                                else mw.config.default_engine)
        return mw.engines.render(self.template, displays_on, {'w':self})

    @classmethod
    def idisplay(cls, displays_on=None, **kw):
        """Initialise and display the widget. This intended for simple widgets
        that don't need a value from the controller."""
        return cls.req(**kw).display(displays_on)

    @classmethod
    def validate(cls, params):
        if cls.parent:
            raise core.WidgetError('Only call validate on root widgets')
        value = vd.unflatten_params(params)
        try:
            if cls.id:
                value = value[cls.id]
        except KeyError:
            raise vd.ValidationError('corrupt', cls.validator, widget=cls.req())
        ins = cls.req()
        core.request_local()['validated_widget'] = ins
        return ins._validate(value)

    @vd.catch_errors
    def _validate(self, value):
        self._validated = True
        self.value = value
        return self.validator.to_python(value)

class LeafWidget(Widget):
    """
    A widget that has no children; this is the most common kind, e.g. form
    fields.
    """


class WidgetBunch(tuple):
    def __getattr__(self, id):
        for w in self:
            if w.id == id:
                return w
        raise AttributeError("Widget has no child named '%s'" % id)


class CompoundWidget(Widget):
    """
    A widget that has an arbitrary number of children, this is common for
    layout components, such as :class:`tw.forms.TableLayout`.
    """
    children = pm.Param('Children for this widget. This must be an interable, each item of which is a Widget')
    c = pm.Variable("Alias for children", default=property(lambda s: s.children))
    children_deep = pm.Variable("Children, including any children from child CompoundWidgets that have no id")
    template = 'genshi:tw.core.templates.display_children'

    @classmethod
    def post_define(cls, cls2=None):
        cls = cls2 or cls
        Widget.post_define(cls)
        cls._sub_compound = not cls.id_elem
        if not hasattr(cls, 'children'):
            return
        ids = set()
        joined_cld = []
        cls.resources = set(cls.resources)
        for c in cls.children:
            if not issubclass(c, Widget):
                raise pm.ParameterError("All children must be widgets")
            if c.id:
                if c.id in ids:
                    raise core.WidgetError("Duplicate id '%s'" % c.id)
                ids.add(c.id)
            if c.resources: # TBD: this shouldn't be needed
                cls.resources.update(c.resources)
            joined_cld.append(c(parent=cls, resources=[]))
        # TBD: check for dupes in _sub_compound
        cls.children = WidgetBunch(joined_cld)

    def __init__(self, **kw):
        super(CompoundWidget, self).__init__(**kw)
        self.children = WidgetBunch(c.req(parent=weakref.proxy(self)) for c in self.children)

    def prepare(self):
        super(CompoundWidget, self).prepare()
        v = self.value or {}
        if isinstance(v, dict):
            for c in self.children:
                c.value = v.get(c.id)
        else:
            for c in self.children:
                c.value = getattr(v, c.id, None)

    @vd.catch_errors
    def _validate(self, value):
        self._validated = True
        value = value or {}
        if not isinstance(value, dict):
            raise vd.ValidationError('corrupt', self.validator)
        self.value = value
        any_errors = False
        data = {}
        for c in self.children:
            try:
                if c._sub_compound:
                    data.update(c._validate(value))
                else:
                    data[c.id] = c._validate(value.get(c.id))
            except vd.ValidationError:
                data[c.id] = vd.Invalid
                any_errors = True
        self.validator.validate_python(data)
        if any_errors:
            raise vd.ValidationError('childerror', self.validator)
        return data

class RepeatingWidgetBunchCls(object):
    def __init__(self, parent):
        self.parent = parent
        self._repetition_cache = {}
    def __getitem__(self, item):
        if not isinstance(item, int):
            raise KeyError("Must specify an integer")
        try:
            rep = self._repetition_cache[item]
        except KeyError:
            rep = self.parent.child(parent=self.parent, repetition=item, id_elem=str(item))
            self._repetition_cache[item] = rep
        return rep

class RepeatingWidgetBunch(object):
    def __init__(self, parent, rwbc):
        self.parent = parent
        self.rwbc = rwbc
        self._repetition_cache = {}
    def __len__(self):
        return self.parent.repetitions
    def __iter__(self):
        for i in xrange(len(self)):
            yield self[i]
    def __getitem__(self, item):
        if not isinstance(item, int):
            raise KeyError("Must specify an integer")
        try:
            rep = self._repetition_cache[item]
        except KeyError:
            rep = self.rwbc[item].req(parent=weakref.proxy(self.parent))
            self._repetition_cache[item] = rep
        return rep


class RepeatingWidget(Widget):
    """
    A widget that has a single child, which is repeated an arbitrary number
    of times, such as :class:`tw.forms.GridLayout`.
    """
    child = pm.Param('Child for this widget. This must be a Widget.')
    repetitions = pm.Param('Fixed number of repetitions. If this is None, it dynamically determined, based on the length of the value list.', default=None)
    min_reps = pm.Param('Minimum number of repetitions', default=None)
    max_reps = pm.Param('Maximum number of repetitions', default=None)
    extra_reps = pm.Param('Number of extra repeitions, beyond the length of the value list.', default=1)

    children = pm.Variable()
    repetition = pm.ChildVariable('The repetition of a child widget.')

    template = 'genshi:tw.core.templates.display_children'

    @classmethod
    def post_define(cls, cls2=None):
        cls = cls2 or cls
        Widget.post_define(cls)
        if not hasattr(cls, 'child'):
            return
        if not issubclass(cls.child, Widget):
            raise pm.ParameterError("Child must be a widget")
        if cls.child.id_elem:
            raise pm.ParameterError("Child must have no id")
        cls.resources = set(cls.resources)
        cls.resources.update(cls.child.resources)
        cls.child = cls.child(parent=cls, resources=[])
        cls.children = RepeatingWidgetBunchCls(parent=cls)

    def __init__(self, **kw):
        super(RepeatingWidget, self).__init__(**kw)
        self.children = RepeatingWidgetBunch(self, self.children)

    def prepare(self):
        super(RepeatingWidget, self).prepare()
        value = self.value or []
        if self.repetitions is None:
            reps = len(value) + self.extra_reps
            if self.max_reps is not None and reps > self.max_reps:
                reps = self.max_reps
            if self.min_reps is not None and reps < self.min_reps:
                reps = self.min_reps
            self.repetitions = reps
        for i,v in enumerate(value):
            self.children[i].value = v

    @vd.catch_errors
    def _validate(self, value):
        value = value or []
        if not isinstance(value, list):
            raise vd.ValidationError('corrupt', self.validator)
        self.value = value
        self.repetitions = len(value) # TBD
        any_errors = False
        data = []
        for i,v in enumerate(value):
            try:
                data.append(self.children[i]._validate(v))
            except vd.ValidationError:
                data.append(vd.Invalid)
                any_errors = True
        self.validator.validate_python(data)
        if any_errors:
            raise vd.ValidationError('childerror', self.validator)
        return data


class DisplayOnlyWidget(Widget):
    """
    A widget that is used only for display purposes; it does not affect value
    propagation or validation. This is used by widgets like
    :class:`tw.forms.FieldSet` that surround a group of widgets in a wrapper,
    without otherwise affecting the behaviour.
    """
    child = pm.Param('Child for this widget. This must be a widget.')
    id = None

    @classmethod
    def post_define(cls, cls2=None):
        cls = cls2 or cls
        Widget.post_define(cls)
        if not hasattr(cls, 'child'):
            return
        if not issubclass(cls.child, Widget):
            raise pm.ParameterError("Child must be a widget")
        cls._sub_compound = cls.child._sub_compound
        if cls.child.resources:
            cls.resources = set(cls.resources).update(cls.child.resources)
        cls.id = cls.child.id
        cls.id_elem = None
        cls.child = cls.child(parent=cls, resources=[])

    def __init__(self, **kw):
        super(DisplayOnlyWidget, self).__init__(**kw)
        self.child = self.child.req(parent=weakref.proxy(self))

    def prepare(self):
        super(DisplayOnlyWidget, self).prepare()
        self.child.value = self.value

    def _validate(self, value):
        return self.child._validate(value)


class WidgetListMeta(type):
    """Metaclass for WidgetList."""
    def __new__(meta, name, bases, dct):
        children = []
        if name != 'WidgetList':
            for b in bases:
                children.extend(getattr(b, 'children', []))
            for d, v in dct.items():
                 if issubclass(v, Widget):
                    children.append(v(id=d))
                 else:
                    raise core.WidgetError('All members of a WidgetList must be widgets.')
            children.sort(key=lambda w: w._seq)
        widget = type.__new__(meta, name, bases, {'children':children})


class WidgetList(object):
    """
    This lets you define a list of widgets declaratively; use it like::

        class MyWidgets(twc.WidgetList):
            a = TextField()
            b = Label(text='a')

    The class is then iterable, so it can be passed as the :attr:`children`
    parameter to :class:`CompoundWidget`. It also supports addition (e.g.
    MyWidgets + MyWidgets2 returns the concatonated list). Inheritence has
    a similar effect.

    Note: ordering, which uses :attr:`_seq`.
    """
    __metaclass__ = WidgetListMeta

    @classmethod
    def __iter__(self):
        return self.children.__iter__()

    @classmethod
    def __add__(self, other):
        if isinstance(other, WidgetList):
            other = other.children
        return self.children + other
