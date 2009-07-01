ToscaWidgets History
====================

Python web widgets were pioneered in TurboGears and many of the key ideas remain. Once the value of widgets was realised, a move was made to create a separate library, this is ToscaWidgets. The key differences are:

 * ToscaWidget is framework independent.
 * Multiple template engines are supported.
 * Resource links are injected by rewriting the page on output.
 * The forms library is separate from the core widget library.
 * The tw namespace exists for widget libraries to be located in.

ToscaWidgets had some success, but did not gain as much usage as hoped, in part due to a lack of documentation in the beginning. Over time, several moves were made to simplify the library. ToscaWidgets 2 is an attempt to simplify widgets even further - at the cost of breaking backward-compatibility. The key differences are:

 * A widget instance is now created for each request.
 * In widget libraries, parameters are defined declaratively.
 * In widget templates, the widget is available as ``$w``. By default, parameters must be accessed as ``$w.param`` although the *params_as_vars* config option allows ``$param`` as in ToscaWidgets 0.9.
 * Validation is done in the core widget library, and no longer relies on FormEncode.
 * Declarative instantiation of widgets has been made more concise.
 * Framework interfaces are almost completely removed; ToscaWidgets is just a piece of WSGI middleware.
 * The namespace is now tw2

Some minor differences to be aware of:

 * There is no automatic calling of parameters; you must explicitly use :class:`tw2.core.Deferred` for this.
 * A widget does not automatically get the ``resources`` from its base class.
 * engine_name is compulsory for templates, and there are no inline templates (yet, may be added later).
 * ToscaWidgets 2 requires Python 2.5. Suppot for 2.4 and 2.6 is planned.
 * tw.api has been removed; just use tw2.core
 * The compound ID separator is now a colon (:) and IDs may not contain colons.
 * The toscasidgets simple template engine has been removed.
 * Widget.__call__ is no longer an alias for display, as this causes problems for Cheetah.

In tw2.forms
 * name is always identical to id
 * Simpler inheritence tree


Dynamic Parameters
------------------

One of the main challenges for a widget framework is that some widget parameters are fixed for the life of the app, while some change with each request.

In ToscaWidgets 0.9, widget instances existed for the life of the app. It was important to never update a widget parameter within a request, as this would break thread-safety. Instead, per-request parameters were stored in a dictionary. However, this is inconvenient, particularly when setting parameters on widgets deep within a nested hierarchy. It requires the user to create a singleton instance of every widget. It is also a potential performance problem.

The first attempt at ToscaWidgets 2 also had widget instances exist for the life of the app. However, instrumentation of the class made some parameters request local. This makes accessing parameters much more convenient. However, you still need to create singleton instances of every widget, and it is still a potential peformance problem.

The second attempt at ToscaWidgets 2 has widget instances exist only for the life of a request. All fixed parameters are set by subclassing widgets. This keeps parameters easy to access, and avoids the need to create singletons. Whether it is a performance problem is still being established.
