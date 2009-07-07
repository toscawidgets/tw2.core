import copy, weakref, re, itertools, webob
import template, core, util, validation as vd, params as pm

try:
    import formencode
except ImportError:
    formencode = None

reserved_names = ('parent', 'demo_for', 'child', 'submit')
_widget_seq = itertools.count(0)

class WidgetMeta(pm.ParamMeta):
    """
    This metaclass:

     * Detects members that are widgets, and constructs the
       `children` parameter based on this.
     * Gives widgets a sequence number, so ordering works correctly.
     * Calls post_define for the widget class and base classes. This
       is needed as it's not possible to call super() in post_define.
    """
    def __new__(meta, name, bases, dct):
        if name != 'Widget' and 'children' not in dct:
            new_children = []
            for d, v in dct.items():
                if isinstance(v, type) and issubclass(v, Widget) and d not in reserved_names:
                    new_children.append((v, d))
                    del dct[d]
            children = []
            for b in bases:
                bcld = getattr(b, 'children', None)
                if bcld and not isinstance(bcld, RepeatingWidgetBunchCls):
                    children.extend(bcld)
            new_children = sorted(new_children, key=lambda t: t[0]._seq)
            children.extend(hasattr(v, 'id') and v or v(id=d) for v,d in new_children)
            if children:
                dct['children'] = children
        widget = super(WidgetMeta, meta).__new__(meta, name, bases, dct)
        widget._seq = _widget_seq.next()
        for w in reversed(widget.__mro__):
            if 'post_define' in w.__dict__:
                w.post_define.im_func(widget)
        return widget

class Widget(pm.Parametered):
    """
    Base class for all widgets.
    """
    __metaclass__ = WidgetMeta

    id = pm.Param('Widget identifier', request_local=False)
    template = pm.Param('Template file for the widget, in the format engine_name:template_path.')
    validator = pm.Param('Validator for the widget.', default=None, request_local=False)
    attrs = pm.Param("Extra attributes to include in the widget's outer-most HTML tag.", default={})
    value = pm.Param("The value for the widget.", default=None)
    resources = pm.Param("Resources used by the widget. This must be an iterable, each item of which is a :class:`Resource` subclass.", default=[], request_local=False)

    error_msg = pm.Variable("Validation error message.")
    parent = pm.Variable("The parent of this widget, or None if this is a root widget.")

    _sub_compound = False
    _valid_id_re = re.compile(r'^[\w\-\_\.]*$')


    @classmethod
    def req(cls, **kw):
        """
        Generate an instance of the widget.
        """
        ins = object.__new__(cls)
        ins.__init__(**kw)
        return ins

    def __new__(cls, **kw):
        """
        New is overloaded to return a subclass of the widget, rather than an instance.
        """
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
                    id = getattr(cls,  'id', None)
                    if id and not id.startswith('my'):
                        raise pm.ParameterError("id must start with 'my'")

        post_define should always cope with missing data - the class may be an
        abstract class. There is no need to call super(), the metaclass will do
        this automatically.
        """
        if getattr(cls, 'id', None) and not cls._valid_id_re.match(cls.id):
            raise pm.ParameterError("Not a valid identifier: '%s'" % cls.id)
        cls._gen_compound_id()
        cls._auto_register()
        if cls.validator:
            if cls.validator is pm.Required:
                vld = cls.__mro__[1].validator
                cls.validator = vld and vld.clone(required=True) or vd.Validator(required=True)
            if isinstance(cls.validator, type) and issubclass(cls.validator, vd.Validator):
                cls.validator = cls.validator()
            if not isinstance(cls.validator, vd.Validator) and not (
                    formencode and isinstance(cls.validator, formencode.Validator)):
                raise pm.ParameterError("Validator must be either a tw2 or FormEncode validator")

        cls._deferred = [a for a in dir(cls) if isinstance(getattr(cls, a), pm.Deferred)]
        cls._attr = [p.name for p in cls._params.values() if p.attribute]

        if cls.parent:
            for p in cls.parent._all_params.values():
                if p.child_param and not hasattr(cls, p.name) and p.default is not pm.Required:
                    setattr(cls, p.name, p.default)

    @classmethod
    def _gen_compound_id(cls):
        ancestors = []
        cur = cls
        while cur:
            if cur in ancestors:
                raise core.WidgetError('Parent loop')
            ancestors.append(cur)
            cur = cur.parent
        elems = reversed(filter(None, [a._compound_id_elem() for a in ancestors]))
        cls.compound_id = elems and ':'.join(elems) or None
        cls.attrs = cls.attrs.copy()
        cls.attrs['id'] = getattr(cls, 'id', None) and cls.compound_id

    @classmethod
    def _compound_id_elem(cls):
        return getattr(cls, 'id', None)

    @classmethod
    def _auto_register(cls):
        if hasattr(cls, 'request') and getattr(cls, 'id', None):
            import middleware
            capp = getattr(cls.__module__, 'tw2_controllers', middleware.global_controllers)
            if capp:
                capp.register(cls, cls.id)

    def prepare(self):
        """
        This is an instance method, that is called just before the Widget is
        displayed. Process request-local configuration here. For
        efficiency, widgets should do as little work as possible here.
        Use it like this::

            class MyWidget(Widget):
                def prepare(self):
                    super(MyWidget, self).prepare()
                    self.value = 'My: ' + str(self.value)
        """
        for a in self._deferred:
            dfr = getattr(self, a)
            if isinstance(dfr, pm.Deferred):
                setattr(self, a, dfr.fn())
        if self.validator and not hasattr(self, '_validated'):
            self.value = self.validator.from_python(self.value)
        if self._attr or 'attrs' in self.__dict__:
            self.attrs = self.attrs.copy()
            self.attrs['id'] = getattr(self, 'id', None) and self.compound_id
            for a in self._attr:
                if a in self.attrs:
                    raise pm.ParameterError("Attribute parameter clashes with user-supplied attribute: '%s'" % a)
                self.attrs[self._params[a].view_name] = getattr(self, a)

    @util.class_or_instance
    def display(self, cls, displays_on=None, **kw):
        """Display the widget - render the template. In the template, the
        widget instance is available as the variable ``$w``.

        If display is called on a class, it automatically creates an instance.

        `displays_on`
            The name of the template engine this widget is being displayed
            inside. If not specified, this is determined automatically, from
            the parent's template engine, or the default, if there is no
            parent. Set this to ``string`` to get raw string output.
        """
        if not self:
            vw = core.request_local().get('validated_widget')
            if vw:
                return vw.display()
            else:
                return cls.req(**kw).display(displays_on)
        else:
            if not self.parent:
                self.prepare()
            if self.resources:
                self.resources = WidgetBunch([r.req() for r in self.resources])
                for r in self.resources:
                    r.prepare()
                core.request_local().setdefault('resources', set()).update(self.resources)
            mw = core.request_local().get('middleware')
            if displays_on is None:
                displays_on = (self.parent.template.split(':')[0] if self.parent
                                                    else (mw and mw.config.default_engine or 'string'))
            v = {'w':self}
            if mw and mw.config.params_as_vars:
                for p in self._params:
                    if hasattr(self, p):
                        v[p] = getattr(self, p)
            eng = mw and mw.engines or template.global_engines
            return eng.render(self.template, displays_on, v)

    @classmethod
    def validate(cls, params, state=None):
        """
        Validate form input. This should always be called on a class. It
        either returns the validated data, or raises a
        :class:`ValidationError` exception.
        """
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
        if self.validator:
            value = self.validator.to_python(value)
            if isinstance(self.validator, vd.Validator):
                self.validator.validate_python(value)
            else:
                self.validator.validate_python(value, None)
        return value

    def safe_modify(self, attr):
        if (attr not in self.__dict__ and
                isinstance(getattr(self, attr, None), (dict, list))):
            setattr(self, attr, copy.copy(getattr(self, attr)))

class LeafWidget(Widget):
    """
    A widget that has no children; this is the most common kind, e.g. form
    fields.
    """


class WidgetBunch(list):
    def __getattr__(self, id):
        for w in self:
            if w.id == id:
                return w
        raise AttributeError("Widget has no child named '%s'" % id)


class CompoundWidget(Widget):
    """
    A widget that has an arbitrary number of children, this is common for
    layout components, such as :class:`tw2.forms.TableLayout`.
    """
    children = pm.Param('Children for this widget. This must be an interable, each item of which is a Widget')
    c = pm.Variable("Alias for children", default=property(lambda s: s.children))
    children_deep = pm.Variable("Children, including any children from child CompoundWidgets that have no id")
    template = 'genshi:tw2.core.templates.display_children'

    @classmethod
    def post_define(cls):
        """
        Check children are valid; update them to have a link to the parent.
        """
        cls._sub_compound = not getattr(cls, 'id', None)
        if not hasattr(cls, 'children'):
            return
        ids = set()
        joined_cld = []
        for c in cls.children:
            if not issubclass(c, Widget):
                raise pm.ParameterError("All children must be widgets")
            if getattr(c, 'id', None):
                if c.id in ids:
                    raise core.WidgetError("Duplicate id '%s'" % c.id)
                ids.add(c.id)
            joined_cld.append(c(parent=cls))
        cls.children = WidgetBunch(joined_cld)

    def __init__(self, **kw):
        super(CompoundWidget, self).__init__(**kw)
        self.children = WidgetBunch(c.req(parent=weakref.proxy(self)) for c in self.children)

    def prepare(self):
        """
        Propagate the value for this widget to the children, based on their id.
        """
        super(CompoundWidget, self).prepare()
        v = self.value or {}
        if not hasattr(self, '_validated'):
            if isinstance(v, dict):
                for c in self.children:
                    if c._sub_compound:
                        c.value = v
                    elif c.id in v:
                        c.value = v[c.id]
            else:
                for c in self.children:
                    if c._sub_compound:
                        c.value = v
                    elif hasattr(v, c.id):
                        c.value = getattr(v, c.id)
        for c in self.children:
            c.prepare()

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
                    val = c._validate(value.get(c.id))
                    if val is not vd.EmptyField:
                        data[c.id] = val
            except vd.ValidationError:
                data[c.id] = vd.Invalid
                any_errors = True
        if self.validator:
            data = self.validator.to_python(data)
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
            rep = self.parent.child(parent=self.parent, repetition=item, id=str(item))
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
    of times, such as :class:`tw2.forms.GridLayout`.
    """
    child = pm.Param('Child for this widget. The child must have no id.')
    repetitions = pm.Param('Fixed number of repetitions. If this is None, it dynamically determined, based on the length of the value list.', default=None)
    min_reps = pm.Param('Minimum number of repetitions', default=None)
    max_reps = pm.Param('Maximum number of repetitions', default=None)
    extra_reps = pm.Param('Number of extra repeitions, beyond the length of the value list.', default=0)
    children = pm.Param('children specified for this widget will be passed to the child. In the template, children gets the list of repeated childen.', default=[])

    repetition = pm.ChildVariable('The repetition of a child widget.')

    template = 'genshi:tw2.core.templates.display_children'

    @classmethod
    def post_define(cls):
        """
        Check child is valid; update with link to parent.
        """
        if not hasattr(cls, 'child'):
            return
        if getattr(cls, 'children', None):
            cls.child = cls.child(children = cls.children)
            cls.children = []
        if not issubclass(cls.child, Widget):
            raise pm.ParameterError("Child must be a widget")
        if getattr(cls.child, 'id', None):
            raise pm.ParameterError("Child must have no id")
        cls.child = cls.child(parent=cls)
        cls.rwbc = RepeatingWidgetBunchCls(parent=cls)

    def __init__(self, **kw):
        super(RepeatingWidget, self).__init__(**kw)
        self.children = RepeatingWidgetBunch(self, self.rwbc)

    def prepare(self):
        """
        Propagate the value for this widget to the children, based on their index.
        """
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
        for c in self.children:
            c.prepare()

    @vd.catch_errors
    def _validate(self, value):
        self._validated = True
        value = value or []
        if not isinstance(value, list):
            raise vd.ValidationError('corrupt', self.validator, self)
        self.value = value
        any_errors = False
        data = []
        for i,v in enumerate(value):
            try:
                data.append(self.children[i]._validate(v))
            except vd.ValidationError:
                data.append(vd.Invalid)
                any_errors = True
        if self.validator:
            data = self.validator.to_python(data)
            self.validator.validate_python(data)
        if any_errors:
            raise vd.ValidationError('childerror', self.validator, self)
        return data


class DisplayOnlyWidget(Widget):
    """
    A widget that has a single child. The parent widget is only used for display
    purposes; it does not affect value propagation or validation. This is used
    by widgets like :class:`tw2.forms.FieldSet`.
    """
    child = pm.Param('Child for this widget.')
    children = pm.Param('children specified for this widget will be passed to the child', default=[])

    @classmethod
    def post_define(cls):
        if not getattr(cls, 'child', None):
            return
        if getattr(cls, 'children', None):
            cls.child = cls.child(children = cls.children)
            cls.children = []
        if not issubclass(cls.child, Widget):
            raise pm.ParameterError("Child must be a widget")
        cls._sub_compound = cls.child._sub_compound
        cls_id = getattr(cls, 'id', None)
        child_id = getattr(cls.child, 'id', None)
        if cls_id and child_id and cls_id != child_id:
            raise pm.ParameterError("Can only specify id on either a DisplayOnlyWidget, or its child, not both: '%s' '%s'" % (cls_id, child_id))
        if not cls_id and child_id:
            cls.id = child_id
            cls._gen_compound_id()
            cls.child = cls.child(parent=cls)
        else:
            cls.child = cls.child(id=cls_id, parent=cls)

    @classmethod
    def _compound_id_elem(cls):
        return None

    def __init__(self, **kw):
        super(DisplayOnlyWidget, self).__init__(**kw)
        if hasattr(self, 'child'):
            self.child = self.child.req(parent=weakref.proxy(self))
        else:
            self.child = None

    def prepare(self):
        super(DisplayOnlyWidget, self).prepare()
        if self.child:
            if not hasattr(self, '_validated'):
                self.child.value = self.value
            self.child.prepare()

    @vd.catch_errors
    def _validate(self, value):
        self._validated = True
        try:
            return self.child._validate(value)
        except vd.ValidationError, e:
            raise vd.ValidationError('childerror', self.validator, self)

class Page(DisplayOnlyWidget):
    """
    An HTML page. This widget includes a :meth:`request` method that serves
    the page.
    """
    title = pm.Param('Title for the page')
    template = "genshi:tw2.core.templates.page"
    _no_autoid = True

    @classmethod
    def post_define(cls):
        if not getattr(cls, 'id', None) and '_no_autoid' not in cls.__dict__:
            cls.id = cls.__name__.lower()
            cls._auto_register()
            DisplayOnlyWidget.post_define.im_func(cls)

    @classmethod
    def request(cls, req):
        resp = webob.Response(request=req, content_type="text/html; charset=UTF8")
        ins = cls.req()
        ins.fetch_data(req)
        resp.body = ins.display().encode('utf-8')
        return resp

    def fetch_data(self, req):
        pass
