Future Features
---------------

Client-Side Validation
======================

There are two points at which client-side validation can be done:

 * onblur - when the user leaves the field
 * onsubmit - when the form is submitted

Checks that apply to the whole form can only be done onsubmit. It's best not to report missing fields as an error during onblur, so this is only done onsubmit.

Some checks cannot be done client-side, e.g. checking if a user name is taken. In these cases, onblur checking is possible, using an Ajx request. Ajax checking at onsubmit is not done - it's better to just submit, and rely on server-side validation.

One important principle is that the JavaScript validator should always behave exactly the same as the Python validator. This may be difficult to achieve with date/time fields.


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


Widget has a method, :meth:`link(**kw)` to generate a link to the controller method, with any desired parameters. When a link is generated, the widget is registered with the ToscaWidgets middleware. Requests to ``/controllers/my_widget`` will result in the controller method being called.


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

tw2.auth
========

The aim is to have an authentication system that takes a more "batteries included" approach than libraries like repoze.who. Features to include are:

 * User registration, with email verification
 * Forgotten password
 * Account lockouts to prevent brute force attacks
 * Change password, with password strength checking
 * "Remember me"
 * Post-login messages
 * Single sign-on - OpenID, Windows domain authentication, etc.
 * User is informed of the previous login time
 * Administrator can disable accounts

**Security Policies**

We want to provide sensible defaults for all the options. However, different sites will have different security requirements. One approach is to have two basic security policies:

`Regular`
    This would be appropriate for most sites that do not process money or especially sensitive data. Potential defaults:

     * Six character passwords, without complexity checking
     * "Forgotten password" only requires email verification.
     * Two hours inactivity timeout.
     * "Remember me" is allowed

`High`
    This would be appropriate for more sensitive sites. Of course, highly sensitive sites, such as online banking, would consider the individual options carefully and not just use the defaults. Potential defaults:

    * Eight character passwords, with complexity checking
    * "Forgotten password" uses personal questions (e.g. "Mother's maiden name") as well as email verification.
    * 15 minutes inactivity timeout
    * "Remember me" is not allowed; login form has "autocomplete=False".


**Extra Security Features**

The library could provide features for higher security:

`Challenge passwords`
    At login, the user is asked to enter, say, characters 1, 3 and 7 from the password. This stops someone being able to capture the whole password from a single login.

`Password rotation`
    Users are forced to change password periodically, perhaps every six months.

`End device compliance checking`
    Before login is allowed, the site checks that the client is secure. Simple checks could be performed using JavaScript, to determine is the browser is up-to-date. More complex checks could be performed using Flash/Java/ActiveX to confirm the operating system is up-to-date, anti-virus is installed, etc.

`Extra login checks`
    This could include source IP address, SSL client certificates, or long-lived cookies. For example, administrator logins could be restricted to a particular source IP address. Or an application could be restricted to company-owned clients, by installing a long-lived cookie on the clients, which is required for login.

`Geolocation`
    When a login comes from a country that the user does not normally login from, extra security checks are performed.

