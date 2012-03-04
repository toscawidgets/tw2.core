Standalone Tutorial
===================

.. note::
    The files created in this tutorial can be downloaded as
    a :download:`.zip file <standalone.zip>`.

Installing ToscaWidgets2
------------------------

Your operating system may provide another way of installing ToscaWidgets2
(`yum`, `apt-get`, etc...).  Failing that, you can use `pip`::

    $ pip install tw2.core tw2.forms tw2.dynforms tw2.devtools tw2.sqla

TW2 supports many different `templating engines`.  For this tutorial we'll be
writing ``genshi`` templates, so install support for that as well::

    $ pip install genshi

In this tutorial, we're also going to be showing off some of the database
features of ``tw2.sqla``.  For our application we're going to use ``elixir``;
install it too::

    $ pip install elixir

Building a Page
---------------

To get started, we'll build a simple "Hello World" application.  First,
create ``myapp.py`` with the following::

    import tw2.core
    import tw2.devtools

    class Index(tw2.core.Page):
        template = 'genshi:./index.html'

    tw2.devtools.dev_server()

Here were are creating a Page widget, called Index, with a template specified.
Index is a special name that matches the root URL. We need to create the
template, so in the same directory, create ``index.html`` with the following
content::

    <html xmlns="http://www.w3.org/1999/xhtml"
          xmlns:py="http://genshi.edgewall.org/">
        <head>
            <title>My Application</title>
        </head>
        <body>
            <h1>My Application</h1>
            <p>Hello World!</p>
        </body>
    </html>

This is a `Genshi <http://genshi.edgewall.org/>`_ template. This simple
example just uses static HTML, but the template system has many other
features to explore. Now, start the application::

    python myapp.py

And browse to ``http://localhost:8000/`` to check that it's working.

To go beyond simple static HTML, the first step is to have Python code
executed when the page is generated. The ``fetch_data`` method is
called at this time, and we can override this to hook the event. We
will add simple code that reflects the received request. Add the
following to `Index` in ``myapp.py``::

    def fetch_data(self, req):
        self.req = str(req)

The ``req`` variable supplied is a `WebOb
<http://pythonpaste.org/webob/>`_ ``Request`` object. To access a URL
parameter, use ``req.GET['myparam']``. In this example, we simply use
the string representation of the request.

And in ``index.html``, change the ``<p>Hello World!</p>`` line to::

    <pre>$w.req</pre>

The ``$w`` variable refers to the Python widget object that called the template.

Restart the application and refresh your browser to see this.


Building a Form
---------------

We'll now create a simple form. In this example we're going to create a
movie database. First, add to the top of ``myapp.py``::

    import tw2.forms

Now, add another class to this file, before ``tw2.devtools.dev_server()``::

    class Movie(tw2.forms.FormPage):
        title = 'Movie'
        class child(tw2.forms.TableForm):
            title = tw2.forms.TextField(validator=tw2.core.Required)
            director = tw2.forms.TextField()
            genre = tw2.forms.CheckBoxList(
                options=['Action', 'Comedy', 'Romance', 'Sci-fi'])
            class cast(tw2.forms.GridLayout):
                extra_reps = 5
                character = tw2.forms.TextField()
                actor = tw2.forms.TextField()

Before we explain this code, restart the application and browse to
``http://localhost:8000/movie`` to see how the form looks. Have a go an
entering values and submitting; notice the difference when you specify a
title compared to not.

The `FormPage` widget adds functionality beyond `Page` in that it handles
POST requests and redisplays the form on validation failures. The `TableForm`
widget displays the form, including the submit button, and does the table
layout. The form fields are specified in a fairly self-explanatory manner,
noting that validation is specified for `title`. Here, `GridLayout` is used
as a kind of sub-form, which allows multiple cast members to be specified.

The form does not look particularly appealing. To try to improve this, lets
add some CSS. We'll start with something simple; create ``myapp.css`` with
the following::

    th {
        vertical-align: top;
        text-align: left;
        font-weight: normal;
    }

    ul {
        list-style-type: none;
    }

    .required th {
        font-weight: bold;
    }

Notice the use of the "required" class. TableForm applies this to rows that
contain a field that is required.

Before TableForm will inject ``myapp.css`` into the page, we'll have to add
it to the list of resources. Add the following to the top of the `Movie`
class definition just above the line ``title = 'Movie'``::

    resources = [tw2.core.CSSLink(filename='myapp.css')]

Restart ``myapp.py`` and browse to ``http://localhost:8000/movie`` to see
the new css in action.


Connecting to a Database
------------------------

.. WARNING -- this section depends on having tw2.sqla>=2.0b4 which is not yet
   released to pypi at the time of this writing.

The next step is to save movies to a database. To do this, we'll use
`SQLAlchemy <http://www.sqlalchemy.org/>`_ and
`Elixir <http://elixir.ematia.de/trac/wiki>`_ to define a database model.
Create ``model.py`` with the following::

    import elixir, tw2.sqla
    elixir.session = tw2.sqla.transactional_session()
    elixir.metadata = elixir.sqlalchemy.MetaData('sqlite:///myapp.db')

This is code is required to set up the database connection. It will use an
SQLite database, ``myapp.db`` in the current directory. Now, add the code
to define our tables (still to ``model.py``)::

    class Movie(elixir.Entity):
        title = elixir.Field(elixir.String)
        director = elixir.Field(elixir.String)
        genre = elixir.ManyToMany('Genre')
        cast = elixir.OneToMany('Cast')

    class Genre(elixir.Entity):
        name = elixir.Field(elixir.String)
        def __unicode__(self):
            return self.name

    class Cast(elixir.Entity):
        movie = elixir.ManyToOne(Movie)
        character = elixir.Field(elixir.String)
        actor = elixir.Field(elixir.String)

Finally, a small piece of boilerplate code is required at the bottom::

    elixir.setup_all()

This defines three tables - Movie, Genre and Cast, with relations
between them. To learn more about the Elixir syntax, read the
`Elixir tutorial <http://elixir.ematia.de/trac/wiki/TutorialDivingIn>`_.
The next step is to create our database. In the python interpreter, issue::

    import model
    model.elixir.create_all()

We'll now add the genres to the database::

    model.Genre(name='Action')
    model.Genre(name='Comedy')
    model.Genre(name='Romance')
    model.Genre(name='Sci-fi')
    model.elixir.session.commit()

Now, exit the Python interpreter, and update ``myapp.py`` to connect the
`Movie` form to the database. At the top of the file add::

    import tw2.sqla
    import model

Replace ``class Movie(tw2.forms.FormPage):`` with::

    class Movie(tw2.sqla.DbFormPage):
        entity = model.Movie

Add a line just below the ``class child(tw2.forms.TableForm):`` line that
reads::

    id = tw2.forms.HiddenField

And replace ``genre = tw2.forms.CheckBoxList(...)`` with::

    genre = tw2.sqla.DbCheckBoxList(entity=model.Genre)

Finally, we need to enable the wrapper that automatically commits
transactions after each request. Replace ``tw2.devtools.dev_server()`` with::

    tw2.devtools.dev_server(repoze_tm=True)

With this done, restart the application and try submitting a movie.


Front Page
----------

We want a front page that provides a list of our movies, and the ability
to click on a movie to edit it. We can use a GridLayout for this; replace
the `Index` class in ``myapp.py`` with::

    class Index(tw2.sqla.DbListPage):
        entity = model.Movie
        title = 'Movies'
        newlink = tw2.forms.LinkField(link='movie', text='New', value=1)
        class child(tw2.forms.GridLayout):
            title = tw2.forms.LabelField()
            id = tw2.forms.LinkField(link='movie?id=$', text='Edit', label=None)

When you browse to /, you will see a list of movies that have been submitted,
and be able to edit each one. When you're done editing, we want to redirect
back to this front page, so add the following to the `Movie` class::

    redirect = '/'

This gives our application just enough functionality to be a basic movie
tracking system.


GrowingGrid
-----------

The list of cast is somewhat limited; there's no easy way to delete a row,
any you can't add more than five people at once. We can use a widget from
tw2.dynforms to improve this. GrowingGridLayout is a dynamic grid that can
grow client-side. Be aware that tw2.dynforms requires your site's visitors
to have JavaScript enabled.

To use this, update ``myapp.py``; at the top of the file add::

    import tw2.dynforms

Replace this::

    class cast(tw2.forms.GridLayout):
        extra_reps = 5

With::

    class cast(tw2.dynforms.GrowingGridLayout):

Finally, change this::

    class child(tw2.forms.TableForm):

To this::

    class child(tw2.dynforms.CustomisedTableForm):

jQuery's jqGrid
---------------

There are a lot of `non-core` TW2 widget libraries out there, and just to give
you a taste, we'll use one to add one more view to our Movie app.

In your handy-dandy terminal, run::

    $ pip install tw2.jqplugins.jqgrid

Go back to editing ``myapp.py`` and add to the top::

    import tw2.jqplugins.jqgrid

And add another two whole classes near the bottom of the file but above
``tw2.devtools.dev_server(repoze_tm=True)``::

    class GridWidget(tw2.jqplugins.jqgrid.SQLAjqGridWidget):
        entity = model.Movie
        excluded_columns = ['id']
        prmFilter = {'stringResult': True, 'searchOnEnter': False}
        pager_options = { "search" : True, "refresh" : True, "add" : False, }
        options = {
            'url': '/db_jqgrid/',
            'rowNum':15,
            'rowList':[15,30,50],
            'viewrecords':True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
        }

    tw2.core.register_controller(GridWidget, 'db_jqgrid')

    class Grid(tw2.core.Page):
        title = 'jQuery jqGrid'
        child = GridWidget
