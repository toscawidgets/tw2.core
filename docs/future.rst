Future Features
---------------

Client-Side Validation
======================

There are two points at which client-side validation can be done:

 * onblur - when the user leaves the field
 * onsubmit - when the form is submitted

Checks that apply to the whole form can only be done onsubmit. It's best not to report missing fields as an error during onblur, so this is only done onsubmit.

Some checks cannot be done client-side, e.g. checking if a user name is taken. In these cases, onblur checking is possible, using an Ajx request. Ajax checking at onsubmit is not done - it's better to just submit, and rely on server-side validation.

TBD: how to implement this?


Performance
===========

**Resources**

Two optimisations have been considered, but discounted for the time being:

 * Resources only being initialised once, at startup time
 * Static resources being optimised by parent widgets taking all the resources of their children, and removing duplicates. This would not be done where the resource has an :attr:`id`, so the widget can still reference that resource.

**Template**

The idea is to combine templates from a set of widgets at startup, so only a single template is rendered to handle a request. For Genshi, the arrangement could work like this:

`DisplayOnlyWidget`
    ``$w.child.display()`` is replaced with the child template, wrapped in a ``<py:with "w.child as w">`` block.

`CompoundWidget`
    Locate a for loop like ``py:for each="var in s.c(hildren)?"``. Unroll this to a series of child templates, wrapped in a with block, just like ``DisplayOnlyWidget``. Also, calls to ``display()`` outside a for loop can be optimised.

`RepeatingWidget`
    Locate the for loop like ``CompoundWidget``, but it is not unrolled. Inside the loop, ``var.display()`` is replaced with the child template, wrapped in a with block.


Widgets as Controllers
======================

:meth:`controller` is in instance method, so it gets ``self``. This is a different request to where the widget was displayed however, request-local variables are separate. You can use the session to pass state if required.


Widget has a method, :meth:`link(**kw)` to generate a link to the controller method, with any desired parameters. When a link is generated, the widget is registered with the ToscaWidgets middleware. Requests to ``/controllers/my_widget`` will result in the controller method being called::


Security Model
~~~~~~~~~~~~~~

There are three ways to secure a controller method:

`Open`
    The controller method does no authorization itself. It is still subject to any site-wide security.

`Tokens`
    All requests to the controller method require both a valid session, and an authorisation token. The token is cryptographically generated, based on the URL and session ID. These tokens are automatically added by :meth:`link` when required. This results in an intuitive authorisation system, whereby users are only able to access controller methods that they have been provided a link to. It also protects against cross-site request forgeries, and supports strong logout.

`Custom`
    The user defines a custom function to authorise access. One benefit of this approach is that it can allow users to bookmark pages in the secure area, which is not possible with tokens security.

Tokens is the default. To define custom authorisation, override the :meth:`authorise` method on the widget. To use open authorisation, set ``widget.authorise = None``.

**Global Open Security**

In general, the default is token security. However, you can set the global default to open, using::

    twc.controller_security = False

The code is intended to look alarming, to stop people doing this unless they understand the consequences. However, in some cases this is perfectly acceptable, for example:

 * There is no authentication or authorization at all; the application is intended to be fully open.
 * Site-wide security is in place, and no further authorization is required.

TBD: how do turn tokens on for an individual widget?


Tokens
~~~~~~

A token is cryptographically generated like this::

    md5(server_secret + sessionid + url)

The token is then base64 encoded, and then truncated to the first 10 characters. This is configurable, but that length gives 60-bits of randomness, which is considered enough to stop brute force attacks. A brute-force attack would have to take place online, with each attempt requiring a request to the server. Also, other algorithms were considered (sha1, hmac), but this simple arrangement is considered adequate.

Note: to support this, ideally the sessionid will be non-user-controllable, and have a significant amount of randomness in it. However, if this is not the case, it's not a major risk.

Switchers
~~~~~~~~~

Consider an example sales application, that has a list of customers as the front page. Regular users cannot see customers marked as "sensitive", but users with the "manager" permission can. To implement this:

 1) Create two separate view widgets - CustomerListRegular and CustomerListManager

 2) Create a Switcher widget, like this::

        class CustomerList(tws.Switcher):
            def get_widget(self):
                if session.has_perm('manager')
                    return CustomerListManager
                else:
                    return CustomerListRegular

 3) Use links generated by the switcher widget, ``customer_list.link()``

You can also generate a link directly to the :class:`Switcher` controller method, using ``customer_list.link(switcher=True)``. The controller method issues an HTTP redirect to the appropriate widget.


Example
~~~~~~~

How an application using this could look::

    class CustomerFormManager(twd.AutoForm):
        model = db.Customer

    class CustomerFormRegular(twd.AutoForm):
        model = db.Customer

    class CustomerListManager(twd.FilteringGrid):
        id = lambda v: CustomerFormManager.link(v)

    class CustomerListRegular(twd.FilteringGrid):
        id = lambda v: CustomerFormRegular.link(v)

    class CustomerList(tws.Switcher):
        def get_widget(self):
            if session.has_perm('manager')
                return CustomerListManager
            else:
                return CustomerListRegular
