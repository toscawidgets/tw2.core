from __future__ import absolute_import

import copy
import inspect
import itertools
import re
import uuid
import weakref

import six
import webob
from markupsafe import Markup
from six.moves import filter

from . import core
from . import params as pm
from . import templating, util
from . import validation as vd

try:
    import formencode
except ImportError:
    formencode = None

reserved_names = (
    "parent",
    "demo_for",
    "child",
    "submit",
    "datasrc",
    "newlink",
    "edit",
)
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

    @classmethod
    def _collect_base_children(meta, bases):
        """Collect the children from the base classes"""
        children = []
        for b in bases:
            bcld = getattr(b, "children", None)
            if bcld and not isinstance(bcld, RepeatingWidgetBunchCls):
                children.extend(bcld)
        return children

    def __new__(meta, name, bases, dct):
        if name != "Widget" and "children" not in dct:
            new_children = []
            for d, v in list(dct.items()):
                if isinstance(v, type) and issubclass(v, Widget) and d not in reserved_names:

                    new_children.append((v, d))
                    del dct[d]

            children = meta._collect_base_children(bases)
            new_children = sorted(new_children, key=lambda t: t[0]._seq)
            children.extend(hasattr(v, "id") and v or v(id=d) for v, d in new_children)
            if children:
                dct["children"] = children

        widget = super(WidgetMeta, meta).__new__(meta, name, bases, dct)

        widget._seq = six.advance_iterator(_widget_seq)
        for w in reversed(widget.__mro__):
            if "post_define" in w.__dict__:
                w.post_define.__func__(widget)
        return widget


class Widget(six.with_metaclass(WidgetMeta, pm.Parametered)):
    """
    Base class for all widgets.
    """

    id = pm.Param("Widget identifier", request_local=False)
    key = pm.Param("Widget data key; None just uses id", default=None, request_local=False)
    template = pm.Param(
        "Template file for the widget, in the format "
        + "engine_name:template_path.  If `engine_name` is specified, this "
        + "is interepreted not as a path, but as an *inline template*",
    )
    inline_engine_name = pm.Param(
        "Name of an engine.  If specified, `template` is interpreted as " + "an *inline template* and not a path.",
        default=None,
    )
    validator = pm.Param(
        "Validator for the widget.",
        default=None,
        request_local=False,
    )
    attrs = pm.Param(
        "Extra attributes to include in the widget's outer-most HTML tag.",
        default={},
    )
    css_class = pm.Param(
        "CSS class name",
        default=None,
        attribute=True,
        view_name="class",
    )
    value = pm.Param("The value for the widget.", default=None)
    resources = pm.Param(
        "Resources used by the widget. This must be an iterable, each "
        + "item of which is a :class:`Resource` subclass.",
        default=[],
        request_local=False,
    )

    error_msg = pm.Variable("Validation error message.")
    parent = pm.Variable("The parent of this widget, or None if this is a root widget.")

    _sub_compound = False
    _valid_id_re = re.compile(r"^[a-zA-Z][\w\-\_\.]*$")

    @classmethod
    def req(cls, **kw):
        """
        Generate an instance of the widget.

        Return the validated widget for this request if one exists.
        """

        ins = None

        # Create an instance.  First check for the validated widget.
        vw = vw_class = core.request_local().get("validated_widget")
        if vw:
            # Pull out actual class instances to compare to see if this
            # is really the widget that was actually validated
            if not getattr(vw_class, "__bases__", None):
                vw_class = vw.__class__

            if vw_class is not cls:
                vw = None

            if vw:
                ins = vw
                for key, value in kw.items():
                    setattr(ins, key, value)

        if ins is None:
            # We weren't the validated widget (or there wasn't one), so
            # create a new instance
            ins = object.__new__(cls)
            ins.__init__(**kw)

        return ins

    def __new__(cls, id=None, **kw):
        """
        New is overloaded to return a subclass of the widget, rather than an
        instance.
        """

        # Support backwards compatibility with tw1-style calling
        if id and "id" not in kw:
            kw["id"] = id

        newname = calc_name(cls, kw)
        return type(cls.__name__ + "_s", (cls,), kw)

    def __init__(self, **kw):
        for k, v in six.iteritems(kw):
            setattr(self, k, v)
        self._js_calls = []

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

        if getattr(cls, "id", None):
            if not cls._valid_id_re.match(cls.id):
                # http://www.w3schools.com/tags/att_standard_id.asp
                raise pm.ParameterError("Not a valid W3C id: '%s'" % cls.id)

        if hasattr(cls, "id") and not getattr(cls, "key", None):
            cls.key = cls.id

        cls.compound_id = cls._gen_compound_id(for_url=False)
        if cls.compound_id:
            cls.attrs = cls.attrs.copy()
            cls.attrs["id"] = cls.compound_id

        cls.compound_key = cls._gen_compound_key()

        if hasattr(cls, "request") and getattr(cls, "id", None):
            from . import middleware

            path = cls._gen_compound_id(for_url=True)
            middleware.register_controller(cls, path)

        if cls.validator:
            if cls.validator is pm.Required:
                vld = cls.__mro__[1].validator
                cls.validator = vld and vld.clone(required=True) or vd.Validator(required=True)

            if isinstance(cls.validator, type) and issubclass(cls.validator, vd.Validator):
                cls.validator = cls.validator()

            if formencode and isinstance(cls.validator, type) and issubclass(cls.validator, formencode.Validator):
                cls.validator = cls.validator()

            if not isinstance(cls.validator, vd.Validator) and not (
                formencode and isinstance(cls.validator, formencode.Validator)
            ):
                raise pm.ParameterError("Validator must be either a tw2 or FormEncode validator")

        cls.resources = [r(parent=cls) for r in cls.resources]
        cls._deferred = [k for k, v in inspect.getmembers(cls) if isinstance(v, pm.Deferred)]
        cls._attr = [p.name for p in cls._params.values() if p.attribute]

        if cls.parent:
            for p in cls.parent._all_params.values():
                if p.child_param and not hasattr(cls, p.name) and p.default is not pm.Required:

                    setattr(cls, p.name, p.default)

    @classmethod
    def _gen_compound_name(cls, attr, for_url):
        ancestors = []
        cur = cls
        while cur:
            if cur in ancestors:
                raise core.WidgetError("Parent loop")
            ancestors.append(cur)
            cur = cur.parent
        elems = reversed(list(filter(None, [a._compound_name_elem(attr, for_url) for a in ancestors])))
        if getattr(cls, attr, None) or (cls.parent and issubclass(cls.parent, RepeatingWidget)):
            return ":".join(elems)
        else:
            return None

    @classmethod
    def _compound_name_elem(cls, attr, for_url):
        if cls.parent and issubclass(cls.parent, RepeatingWidget):
            if for_url:
                return None
            else:
                return str(getattr(cls, "repetition", None))
        else:
            return getattr(cls, attr, None)

    @classmethod
    def _compound_id_elem(cls, for_url):
        return cls._compound_name_elem("id", for_url)

    @classmethod
    def _gen_compound_id(cls, for_url):
        return cls._gen_compound_name("id", for_url)

    @classmethod
    def _gen_compound_key(cls):
        return cls._gen_compound_name("key", False)

    @classmethod
    def get_link(cls):
        """
        Get the URL to the controller . This is called at run time, not startup
        time, so we know the middleware if configured with the controller path.
        Note: this function is a temporary measure, a cleaner API for this is
        planned.
        """
        if not hasattr(cls, "request") or not getattr(cls, "id", None):
            raise core.WidgetError("Not a controller widget")
        mw = core.request_local()["middleware"]
        return mw.config.controller_prefix + cls._gen_compound_id(for_url=True)

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

        # First, if we don't already have an id, then pick a random one.
        if not hasattr(self, "id"):
            self.id = "id_" + str(uuid.uuid4()).replace("-", "")

        # Then, enforce any params marked with twc.Required.
        for k, v in self._params.items():
            if v.default is pm.Required and not hasattr(self, k):
                raise ValueError("%r is a required Parameter for %r" % (k, self))

        for a in self._deferred:
            dfr = getattr(self, a)
            if isinstance(dfr, pm.Deferred):
                setattr(self, a, dfr.fn())

        if self.validator and not hasattr(self, "_validated"):
            value = self.value

            # Handles the case where FE expects dict-like object, but
            # you have None at your disposal.
            if formencode and isinstance(self.validator, formencode.Validator) and self.value is None:
                value = {}

            try:
                value = self.validator.from_python(value)
            except vd.catch as e:
                value = str(value)
                self.error_msg = e.msg

            if formencode and value == {} and self.value is None:
                value = None

            self.value = value

        if self._attr or "attrs" in self.__dict__:
            self.attrs = self.attrs.copy()
            if self.compound_id:
                self.attrs["id"] = self.compound_id

            for a in self._attr:
                view_name = self._params[a].view_name
                if self.attrs.get(view_name):
                    raise pm.ParameterError("Attr param clashes with user-supplied attr: '%s'" % a)
                self.attrs[view_name] = getattr(self, a)

    def iteritems(self):
        """
        An iterator which will provide the params of the widget in
        key, value pairs.
        """
        for param in self._params.keys():
            value = getattr(self, param)
            yield param, value

    @util.class_or_instance
    def controller_path(self, cls):
        """Return the URL path against which this widget's controller is
        mounted or None if it is not registered with the ControllerApp.
        """

        mw = core.request_local().get("middleware")
        return mw.controllers.controller_path(cls)

    @util.class_or_instance
    def add_call(self, extra_arg, call, location="bodybottom"):
        """
        Not sure what the "extra_arg" needed is for, but it is needed, as is
        the decorator, or an infinite loop ensues.

        Adds a :func:`tw.api.js_function` call that will be made when the
        widget is rendered.
        """
        # log.debug("Adding call <%s> for %r statically.", call, self)
        self._js_calls.append([call, location])

    @util.class_or_instance
    def display(self, cls, value=None, displays_on=None, **kw):
        """Display the widget - render the template. In the template, the
        widget instance is available as the variable ``$w``.

        If display is called on a class, it automatically creates an instance.

        `displays_on`
            The name of the template engine this widget is being displayed
            inside. If not specified, this is determined automatically, from
            the parent's template engine, or the default, if there is no
            parent. Set this to ``string`` to get raw string output.
        """

        # Support backwards compatibility with tw1-style calling
        if value is not None and "value" not in kw:
            kw["value"] = value

        # Support arguments to .display on either instance or class
        # https://github.com/toscawidgets/tw2.core/issues/41
        if self:
            for key, value in kw.items():
                setattr(self, key, value)
        else:
            self = cls.req(**kw)

        # Register any deferred params that are handed to us late in the game
        # (after post_define).  The .prepare method handles processing them
        # later.
        self._deferred += [k for k, v in kw.items() if isinstance(v, pm.Deferred)]

        if not self.parent:
            self.prepare()

        if self._js_calls:
            self.safe_modify("resources")
            # avoids circular reference
            from . import resources as rs

            for item in self._js_calls:
                if "JSFuncCall" in repr(item[0]):
                    self.resources.append(item[0])
                else:
                    self.resources.append(
                        rs._JSFuncCall(
                            src=str(item[0]),
                            location=item[1],
                        )
                    )

        if self.resources:
            self.resources = WidgetBunch([r.req() for r in self.resources])
            for r in self.resources:
                r.prepare()

        return self.generate_output(displays_on)

    def generate_output(self, displays_on):
        """
        Generate the actual output text for this widget.

        By default this renders the widget's template. Subclasses can override
        this method for purely programmatic output.

        `displays_on`
            The name of the template engine this widget is being displayed
            inside.

        Use it like this::

            class MyWidget(LeafWidget):
                def generate_output(self, displays_on):
                    return "<span {0}>{1}</span>".format(self.attrs, self.text)
        """

        mw = core.request_local().get("middleware")

        if not displays_on:
            displays_on = self._get_default_displays_on(mw)

        # Build the arguments used while rendering the template
        kwargs = {"w": self}
        if mw and mw.config.params_as_vars:
            for p in self._params:
                if hasattr(self, p):
                    kwargs[p] = getattr(self, p)

        if self.template is None:
            raise ValueError("A template must be provided.")

        return templating.render(
            self.template,
            displays_on,
            kwargs,
            self.inline_engine_name,
            mw,
        )

    def _get_default_displays_on(self, mw):
        if not self.parent:
            if mw:
                return mw.config.default_engine
            return "string"
        else:
            return templating.get_engine_name(self.parent.template, mw)

    @classmethod
    def validate(cls, params, state=None):
        """
        Validate form input. This should always be called on a class. It
        either returns the validated data, or raises a
        :class:`ValidationError` exception.
        """
        if cls.parent:
            raise core.WidgetError("Only call validate on root widgets")
        value = vd.unflatten_params(params)
        if hasattr(cls, "id") and cls.id:
            value = value.get(cls.id, {})
        ins = cls.req()

        # Key the validated widget by class id
        core.request_local()["validated_widget"] = ins
        return ins._validate(value, state)

    @vd.catch_errors
    def _validate(self, value, state=None):
        """
        Inner validation method; this is called by validate and should not be
        called directly. Overriding this method in widgets is discouraged; a
        custom validator should be coded instead. However, in some
        circumstances overriding is necessary.
        """
        self._validated = True
        self.value = value
        if self.validator:
            value = self.validator.to_python(value, state)
        return value

    def safe_modify(self, attr):
        if attr not in self.__dict__ and isinstance(getattr(self, attr, None), (dict, list)):
            setattr(self, attr, copy.copy(getattr(self, attr)))

    @classmethod
    def children_deep(cls):
        yield cls


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

    children = pm.Param("Children for this widget. This must be an iterable, " + "each item of which is a Widget")
    c = pm.Variable(
        "Alias for children",
        default=property(lambda s: s.children),
    )
    children_deep = pm.Variable(
        "Children, including any children from child " + "CompoundWidgets that have no id",
    )
    template = "tw2.core.templates.display_children"
    separator = pm.Param("HTML snippet which will be inserted " "between each repeated child", default=None)

    @classmethod
    def post_define(cls):
        """
        Check children are valid; update them to have a link to the parent.
        """
        cls._sub_compound = not getattr(cls, "id", None)
        if not hasattr(cls, "children"):
            return
        joined_cld = []

        for c in cls.children:
            if not isinstance(c, type) or not issubclass(c, Widget):
                raise pm.ParameterError("All children must be widgets")
            joined_cld.append(c(parent=cls))

        ids = set()
        for c in cls.children_deep():
            if getattr(c, "id", None):
                if c.id in ids:
                    raise core.WidgetError("Duplicate id '%s'" % c.id)
                ids.add(c.id)
        cls.children = WidgetBunch(joined_cld)
        cls.keyed_children = [c.id for c in joined_cld if hasattr(c, "key") and hasattr(c, "id") and c.key != c.id]

    def __init__(self, **kw):
        super(CompoundWidget, self).__init__(**kw)
        self.children = WidgetBunch(c.req(parent=weakref.proxy(self)) for c in self.children)

    def prepare(self):
        """
        Propagate the value for this widget to the children, based on their id.
        """
        super(CompoundWidget, self).prepare()
        if self.separator:
            self.separator = Markup(self.separator)
        v = self.value or {}
        if not hasattr(self, "_validated"):
            if hasattr(v, "__getitem__"):
                for c in self.children:
                    if c._sub_compound:
                        c.value = v
                    elif c.key in v:
                        c.value = v[c.key]
            else:
                for c in self.children:
                    if c._sub_compound:
                        c.value = self.value
                    else:
                        c.value = getattr(self.value, c.key or "", None)
        for c in self.children:
            c.prepare()

    def get_child_error_message(self, name):
        if isinstance(self.error_msg, six.string_types):
            if self.error_msg.startswith(name + ":"):
                return self.error_msg.split(":")[1]

    @vd.catch_errors
    def _validate(self, value, state=None):
        """
        The value must be a dict, or None. Each item in the dict is passed to
        the corresponding child widget for validation, with special
        consideration for _sub_compound widgets. If a child returns
        vd.EmptyField, that value is not included in the resulting dict at all,
        which is different to including None. Child widgets with a key are
        passed the validated value from the field the key references. The
        resulting dict is validated by this widget's validator. If any child
        widgets produce an errors, this results in a "childerror" failure.
        """
        self._validated = True
        value = value or {}
        if not isinstance(value, dict):
            raise vd.ValidationError("corrupt", self.validator)
        self.value = value
        any_errors = False
        data = {}

        state = util.clone_object(state, full_dict=value, validated_values=data)

        # Validate compound children
        for c in (child for child in self.children if child._sub_compound):
            try:
                data.update(c._validate(value, state))
            except vd.catch as e:
                if hasattr(e, "msg"):
                    c.error_msg = e.msg
                any_errors = True

        # Validate non compound children
        for c in (child for child in self.children if not child._sub_compound):
            d = value.get(c.key, "")
            try:
                val = c._validate(d, data)
                if val is not vd.EmptyField:
                    data[c.key] = val
            except vd.catch as e:
                if hasattr(e, "msg"):
                    c.error_msg = e.msg
                data[c.key] = vd.Invalid
                any_errors = True

        # Validate self, usually a CompoundValidator or a FormEncode form-level
        # validator.
        exception_validator = self.validator
        if self.validator:
            try:
                data = self.validator.to_python(data, state)
            except vd.catch as e:
                # If it failed to validate, check if the error_dict has any
                # messages pertaining specifically to this widget's children.
                error_dict = getattr(e, "error_dict", {})
                if not error_dict:
                    raise

                for c in self.children:
                    if getattr(c, "key", None) in error_dict:
                        c.error_msg = error_dict[c.key]
                        data[c.key] = vd.Invalid
                        exception_validator = None
                        any_errors = True

                # Only re-raise this top-level exception if the validation
                # error doesn't pertain to any of our children.
                if exception_validator:
                    raise

        if any_errors:
            raise vd.ValidationError("childerror", exception_validator)

        return data

    @classmethod
    def children_deep(cls):
        if getattr(cls, "id", None):
            yield cls
        else:
            for c in getattr(cls, "children", []):
                for cc in c.children_deep():
                    yield cc


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
            rep = self.parent.child(parent=self.parent, repetition=item)
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
        for i in range(len(self)):
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

    child = pm.Param("Child for this widget. The child must have no id.")
    repetitions = pm.Param(
        "Fixed number of repetitions. If this is None, it dynamically "
        + "determined, based on the length of the value list.",
        default=None,
    )
    min_reps = pm.Param("Minimum number of repetitions", default=None)
    max_reps = pm.Param("Maximum number of repetitions", default=None)
    extra_reps = pm.Param(
        "Number of extra repeitions, beyond the length of the value list.",
        default=0,
    )
    children = pm.Param(
        "Children specified for this widget will be passed to the child.  "
        + "In the template, children gets the list of repeated childen.",
        default=[],
    )

    repetition = pm.ChildVariable("The repetition of a child widget.")

    template = "tw2.core.templates.display_children"
    separator = pm.Param("HTML snippet which will be inserted " "between each repeated child", default=None)

    @classmethod
    def post_define(cls):
        """
        Check child is valid; update with link to parent.
        """
        if not hasattr(cls, "child"):
            return

        if getattr(cls, "children", None):
            cls.child = cls.child(children=cls.children)
            cls.children = []

        if not isinstance(cls.child, type) or not issubclass(cls.child, Widget):
            raise pm.ParameterError("Child must be a Widget")

        # NOTE: the upstream change was breaking backward compatibility;
        # we are fine with DisplayOnlyWidget in RepeatingWidget

        # if issubclass(cls.child, DisplayOnlyWidget):
        #     raise pm.ParameterError('Child cannot be a DisplayOnlyWidget')

        if getattr(cls.child, "id", None):
            raise pm.ParameterError("Child must have no id")

        cls.child = cls.child(parent=cls)
        cls.rwbc = RepeatingWidgetBunchCls(parent=cls)

    def __init__(self, **kw):
        super(RepeatingWidget, self).__init__(**kw)
        self.children = RepeatingWidgetBunch(self, self.rwbc)

    def prepare(self):
        """
        Propagate the value for this widget to the children, based on their
        index.
        """
        super(RepeatingWidget, self).prepare()
        if self.separator:
            self.separator = Markup(self.separator)
        value = self.value or []
        if self.repetitions is None:
            reps = len(value) + self.extra_reps
            if self.max_reps is not None and reps > self.max_reps:
                reps = self.max_reps
            if self.min_reps is not None and reps < self.min_reps:
                reps = self.min_reps
            self.repetitions = reps

        for i, v in enumerate(value):
            self.children[i].value = v
        for c in self.children:
            c.prepare()
        if not self.repetitions:
            self.children[0].prepare()

    @vd.catch_errors
    def _validate(self, value, state=None):
        """
        The value must either be a list or None. Each item in the list is
        passed to the corresponding child widget for validation. The resulting
        list is passed to this widget's validator. If any of the child widgets
        produces a validation error, this widget generates a "childerror"
        failure.
        """
        self._validated = True
        value = value or []
        if not isinstance(value, list):
            raise vd.ValidationError("corrupt", self.validator, self)
        self.value = value
        any_errors = False
        data = []

        state = util.clone_object(state, full_dict=value, validated_values=data)

        for i, v in enumerate(value):
            try:
                if i == 0 and v is None:
                    data.append(v)
                else:
                    data.append(self.children[i]._validate(v, state))
            except vd.catch:
                data.append(vd.Invalid)
                any_errors = True
        if self.validator:
            data = self.validator.to_python(data, state)
        if any_errors:
            raise vd.ValidationError("childerror", self.validator, self)
        return data


class DisplayOnlyWidgetMeta(WidgetMeta):
    @classmethod
    def _collect_base_children(meta, bases):
        children = []
        for b in bases:
            bchild = getattr(b, "child", None)
            if bchild:
                b = b.child
            bcld = getattr(b, "children", None)
            if bcld and not isinstance(bcld, RepeatingWidgetBunchCls):
                children.extend(bcld)
        return children


def calc_name(cls, kw, char="s"):
    if "parent" in kw:
        newname = kw["parent"].__name__ + "__" + cls.__name__
    else:
        newname = cls.__name__ + "_%s" % char
    return newname


class DisplayOnlyWidget(six.with_metaclass(DisplayOnlyWidgetMeta, Widget)):
    """
    A widget that has a single child. The parent widget is only used for
    display purposes; it does not affect value propagation or validation.
    This is used by widgets like :class:`tw2.forms.FieldSet`.
    """

    child = pm.Param("Child for this widget.")
    children = pm.Param(
        "Children specified for this widget will be passed to the child",
        default=[],
    )
    id_suffix = pm.Variable("Suffix to append to compound IDs", default=None)

    def __new__(cls, **kw):
        newname = calc_name(cls, kw, "d")
        return type(newname, (cls,), kw)

    @classmethod
    def post_define(cls):
        if not getattr(cls, "child", None):
            return

        if getattr(cls, "children", None):
            cls.child = cls.child(children=cls.children)
            cls.children = []

        if getattr(cls, "validator", None):
            cls.child.validator = cls.validator
            cls.validator = None

        if not isinstance(cls.child, type) or not issubclass(cls.child, Widget):
            raise pm.ParameterError("Child must be a widget")

        cls.compound_key = None
        cls._sub_compound = cls.child._sub_compound
        cls_id = getattr(cls, "id", None)
        child_id = getattr(cls.child, "id", None)
        if cls_id and child_id and cls_id != child_id:
            raise pm.ParameterError(
                "Can only specify id on either a DisplayOnlyWidget, or "
                + "its child, not both: '%s' '%s'" % (cls_id, child_id)
            )
        if not cls_id and child_id:
            cls.id = child_id
            DisplayOnlyWidget.post_define.__func__(cls)
            Widget.post_define.__func__(cls)
            cls.child = cls.child(parent=cls, key=cls.key)
        else:
            cls.child = cls.child(id=cls_id, key=cls.key, parent=cls)

    @classmethod
    def _gen_compound_name(cls, attr, for_url):
        elems = [Widget._gen_compound_name.__func__(cls, attr, for_url), getattr(cls, attr, None)]
        elems = list(filter(None, elems))
        if not elems:
            return None
        if not for_url and attr == "id" and getattr(cls, "id_suffix", None):
            elems.append(cls.id_suffix)
        return ":".join(elems)

    @classmethod
    def _compound_name_elem(cls, attr, for_url):
        if cls.parent and issubclass(cls.parent, RepeatingWidget):
            Widget._compound_name_elem.__func__(cls, attr, for_url)
        else:
            return None

    def __init__(self, **kw):
        super(DisplayOnlyWidget, self).__init__(**kw)
        if hasattr(self, "child"):
            self.child = self.child.req(parent=weakref.proxy(self))
        else:
            self.child = None

    def prepare(self):
        super(DisplayOnlyWidget, self).prepare()
        if self.child:
            if not hasattr(self, "_validated"):
                self.child.value = self.value
            self.child.prepare()

    @vd.catch_errorsgit
    def _validate(self, value, state=None):
        self._validated = True
        try:
            return self.child._validate(value, state)
        except vd.ValidationError:
            raise vd.ValidationError("childerror", self.validator, self)

    @classmethod
    def children_deep(cls):
        for c in cls.child.children_deep():
            yield c


def default_content_type():
    "default_content_type"
    return "text/html; charset=%s" % (core.request_local()["middleware"].config.encoding)


class Page(DisplayOnlyWidget):
    """
    An HTML page. This widget includes a :meth:`request` method that serves
    the page.
    """

    title = pm.Param("Title for the page", default=None)
    content_type = pm.Param(
        "Content type header",
        default=pm.Deferred(default_content_type),
        request_local=False,
    )
    template = "tw2.core.templates.page"
    id_suffix = "page"
    _no_autoid = True

    @classmethod
    def post_define(cls):
        if not getattr(cls, "id", None) and "_no_autoid" not in cls.__dict__:
            cls.id = cls.__name__.lower()
            DisplayOnlyWidget.post_define.__func__(cls)
            Widget.post_define.__func__(cls)

    @classmethod
    def request(cls, req):
        ct = cls.content_type
        if isinstance(ct, pm.Deferred):
            ct = ct.fn()
        resp = webob.Response(request=req, content_type=ct)
        ins = cls.req()
        ins.fetch_data(req)
        resp.body = ins.display().encode(core.request_local()["middleware"].config.encoding)
        return resp

    def fetch_data(self, req):
        pass
