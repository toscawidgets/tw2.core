"""
tw2.core contains the base Widgets from which all others are derived.
"""
from core import (WidgetError)

from template import (EngineError)

from params import (Param, ChildParam, Variable, ChildVariable, Required,
    Deferred, ParameterError, Auto)

from widgets import (Widget, CompoundWidget, RepeatingWidget,
    DisplayOnlyWidget, Page)

from resources import (
    JSSymbol,
    Link,
    JSLink,
    CSSLink,
    CSSSource,
    JSSource,
    inject_resources,
    DirLink,
)

from validation import (
    Validator, LengthValidator,
    RegexValidator, IntValidator, OneOfValidator, DateValidator,
    DateTimeValidator, ValidationError, Invalid, EmailValidator,
    UrlValidator, IpAddressValidator, StringLengthValidator,
    ListLengthValidator, RangeValidator, MatchValidator,
    BoolValidator, BlankValidator, safe_validate, EmptyField,
    CompoundValidator,
    Any, All,
)

from middleware import (
    make_middleware,
    dev_server,
    register_controller,
    register_resource,
)

from js import (
    js_symbol,
    js_callback,
    js_function,
    encoder
)

from compat import (
    TGStyleController,
)

from i18n import _, tw2_translation_string

# Shortcut from Deprecated TWEncoder that was in js.py
encode = encoder.encode
