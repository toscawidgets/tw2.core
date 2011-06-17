TurboGears 2 Tutorial
=====================

.. note::
    The files created in this tutorial can be downloaded as a `.zip file
    <https://github.com/ralphbean/tw2.core-docs-turbogears/zipball/master>`_,
    a `.tar file
    <https://github.com/ralphbean/tw2.core-docs-turbogears/tarball/master>`_,
    or can be cloned from a `github repository
    <http://github.com/ralphbean/tw2.core-docs-turbogears>`_.



Enabling ToscaWidgets
---------------------

First, you need to create a TurboGears project. The full instructions are in the `TurboGears documentation <http://www.turbogears.org/2.0/docs/main/QuickStart.html>`_, briefly::

    $ mkvirtualenv --no-site-packages tw2-and-tg
    $ pip install tg.devtools

    $ paster quickstart

    Enter project name: myapp
    Enter package name [myapp]:
    Would you prefer mako templates? (yes/[no]): yes
    Do you need authentication and authorization in this project? ([yes]/no): yes
    ...

    $ cd myapp

Open ``setup.py`` and add the following to the ``install_requires=[...]`` entry::

    install_requires=[

        ...

        "tw2.core",
        "tw2.forms",
        "tw2.dynforms",
        "tw2.sqla",
        "tw2.jqplugins.jqgrid",
        ],

Once that's done.  Install your dependencies by running::

    $ python setup.py develop

There are two different sets of steps to enable ToscaWidgets 2.0 in different versions of TurboGears.  If you don't know what version of TurboGears you have installed, fire up a python interpreter and type::

    >>> import tg
    >>> tg.__version__
    '2.1.1'

If you're using TurboGears 2.1, edit ``myapp/config/app_cfg.py`` and add at the end::

    base_config.use_toscawidgets2 = True

If you're using TurboGears 2.0, instead edit ``myapp/config/middleware.py``, add ``import tw2.core as twc`` to the top of the file, and replace the line::

    app = make_base_app(global_conf, full_stack=True, **app_conf)

with the following two lines::

      custom = lambda app : twc.make_middleware(app, default_engine='mako')
      app = make_base_app(global_conf, wrap_app=custom, full_stack=True, **app_conf)

To check this worked::

    paster serve development.ini


Building a Form
---------------
We'll create a movie database as in the standalone example.  First, let's
create a movie controller and mount it from our root controller.

Create a new file ``myapp/controllers/movie.py`` with the contents::

    from tg import expose, request

    from myapp.lib.base import BaseController
    from myapp import model

    __all__ = ['MovieController']

    import tw2.core
    import tw2.forms

    class MovieForm(tw2.forms.FormPage):
        title = 'Movie'
        class child(tw2.forms.TableForm):
            title = tw2.forms.TextField(validator=tw2.core.Required)
            director = tw2.forms.TextField()
            genres = tw2.forms.CheckBoxList(options=['Action', 'Comedy', 'Romance', 'Sci-fi'])
            class cast(tw2.forms.GridLayout):
                extra_reps = 5
                character = tw2.forms.TextField()
                actor = tw2.forms.TextField()

    class MovieController(BaseController):
        @expose('myapp.templates.widget')
        def movie(self, *args, **kw):
            w = MovieForm(redirect='/movie/').req()
            return dict(widget=w, page='movie')

Add another new file ``myapp/templates/widget.mak`` with the contents::

    <html>
    <%inherit file="local:templates.master"/>

    <%def name="title()">
      TurboGears 2.1 and ToscaWidgets 2, like jelly and jam with no bread:  Great!
    </%def>

    <body>
    ${widget.display()|n}
    </body>
    </html>

And open up the existing file ``myapp/controllers/root.py`` and add,
just below the ``from myapp.controllers.error import ErrorController`` line::

    from myapp.controllers.movie import MovieController

And just below the ``error = ErrorController()`` line::

    movie = MovieController()

With those three file edits in place, you should be able to restart the
application with ``paster serve development.ini`` (there is a ``--reload``
option for convenience) and point your browser
at http://localhost:8080/movie/movie.

The form does not look particularly appealing. To try to improve this, lets
add some CSS. We'll start with something simple;
create ``myapp/public/css/myapp.css`` with the following::

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
it to the list of resources. Add the following to the top of the `MovieForm`
class definition in ``myapp/controllers/movie.py`` just above the line
``title = 'Movie'``::

    resources = [tw2.core.CSSLink(link='/css/myapp.css')]

Restart ``paster`` and browse to http://localhost:8080/movie/movie
to see the new css in action.

Connecting to a Database
------------------------

The next step is to save movies to a database.  To do this, we'll use only
`SQLAlchemy <http://www.sqlalchemy.org/>`_ (and not `elixir
<http://elixir.ematia.de/trac/wiki>`_ as in the standalone tutorial).
SQLAlchemy is built into TurboGears by default.  Edit
``myapp/config/app_config.py`` and add near the top::

    from tw2.core.middleware import ControllersApp as TW2ControllersApp

and add at the very bottom::

    base_config.custom_tw2_config['controllers'] = TW2ControllersApp()
    base_config.custom_tw2_config['controller_prefix'] = '/tw2_controllers/'
    base_config.custom_tw2_config['serve_controllers'] = True

Next add a brand new file ``myapp/model/movie.py`` with the contents::

    from sqlalchemy import Table, ForeignKey, Column
    from sqlalchemy.types import Unicode, Integer
    from sqlalchemy.orm import relation, backref

    from myapp.model import DeclarativeBase, metadata, DBSession

    __all__ = ['Movie', 'Genre', 'Cast']

    movie_genre_table = Table('movie_genre', metadata,
        Column('movie_id', Integer, ForeignKey('movies.id',
            onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
        Column('genre_id', Integer, ForeignKey('genres.id',
            onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    )

    class Movie(DeclarativeBase):
        __tablename__ = 'movies'
        id = Column(Integer, primary_key=True)
        title = Column(Unicode(255))
        director = Column(Unicode(255))

    class Genre(DeclarativeBase):
        __tablename__ = 'genres'
        id = Column(Integer, primary_key=True)
        name = Column(Unicode(255))
        movies = relation('Movie', secondary=movie_genre_table, backref='genres')
        def __unicode__(self):
            return unicode(self.name)

    class Cast(DeclarativeBase):
        __tablename__ = 'casts'
        id = Column(Integer, primary_key=True)
        movie_id = Column(Integer, ForeignKey(Movie.id))
        movie = relation(Movie, backref=backref('cast'))
        character = Column(Unicode(255))
        actor = Column(Unicode(255))

Next edit ``myapp/model/__init__.py`` and uncomment the line that reads::

    DeclarativeBase.query = DBSession.query_property()

and also add the following line to the very bottom of that file::

    from myapp.model.movie import Movie, Genre, Cast

Edit ``myapp/websetup/bootstrap.py`` and add the following just inside the
bootstrap function definition::

    for name in ['Action', 'Comedy', 'Romance', 'Sci-fi']:
        model.DBSession.add(model.Genre(name=name))

And finally, get your controller ready to redirect everything as necessary.
Edit ``myapp/controllers/movie.py`` and add to the very top::

    import tw2.sqla

As well, change ``class MovieForm(tw2.forms.FormPage):`` to instead read::

    class MovieForm(tw2.sqla.DbFormPage):
        entity = model.Movie

Just inside the definition of the child class (right above the ``title =`` line)
add::

    action = '/tw2_controllers/movie_submit'
    id = tw2.forms.HiddenField()

And the last for the `MovieForm`, change ``genres = tw2.forms.CheckBoxList( ... )`` to::

    genres = tw2.sqla.DbCheckBoxList(entity=model.Genre)

And (still in ``myapp/controllers/movie.py``) inside the MovieController's movie method, just below the line ``w = MovieForm(...`` add the three lines::

    w.fetch_data(request)
    mw = tw2.core.core.request_local()['middleware']
    mw.controllers.register(w, 'movie_submit')

Now, in your command prompt run::

    paster setup-app development.ini

This will create and initialize your database in a sqlite DB.

We're almost done, but not quite.  Nonetheless, this is a good point to restart
your app and test to see if any mistakes have cropped up.  Restart `paster`
and visit http://localhost:8080/movie/movie.  Submit your first entry.  It
should give you an `Error 404`, but don't worry.  Point your browser now to
http://localhost:8080/movie/movie?id=1 and you should see the same
movie entry that you just submitted.

Great -- we can write to the database and read back an entry, now how about
a list of entries?

Add a whole new class to ``myapp/controllers/movie.py``::

    class MovieIndex(tw2.sqla.DbListPage):
        entity = model.Movie
        title = 'Movies'
        newlink = tw2.forms.LinkField(link='/movie/movie', text='New', value=1)
        class child(tw2.forms.GridLayout):
            title = tw2.forms.LabelField()
            id = tw2.forms.LinkField(link='/movie/movie?id=$', text='Edit', label=None)

And add the following method to your `MovieController`::

    @expose('myapp.templates.widget')
    def index(self, **kw):
        w = MovieIndex.req()
        w.fetch_data(request)
        return dict(widget=w, page='movie')

Getting Fancy
-------------

And if we wanted to start getting fancy we could add::

    <li><a href="${tg.url('/movie')}" class="${('', 'active')[page=='movie']}">Movies</a></li>

to the list of ``<ul id="mainmenu"> ... </ul>`` items in ``myapp/templates/master.html``.

We could also make things dynamic by editing ``myapp/controllers/movie.py`` and adding at the top::

    import tw2.dynforms

replacing ``class child(tw2.forms.TableForm):`` with::

    class child(tw2.dynforms.CustomisedTableForm):

and replacing::

    class cast(tw2.forms.GridLayout):
        extra_reps = 5

with::

    class cast(tw2.dynforms.GrowingGridLayout):

Getting Fancier
---------------

There are a lot of `non-core` TW2 widget libraries out there, and just to give
you a taste, we'll use one to add one more view to our Movie app.

Edit ``myapp/controllers/movie.py`` and add the following to the top::

    import tw2.jqplugins.jqgrid

Add the following class definition to the same file::

    class GridWidget(tw2.jqplugins.jqgrid.SQLAjqGridWidget):
        id = 'grid_widget'
        entity = model.Movie
        excluded_columns = ['id']
        prmFilter = {'stringResult': True, 'searchOnEnter': False}
        pager_options = { "search" : True, "refresh" : True, "add" : False, }
        options = {
            'url': '/tw2_controllers/db_jqgrid/',
            'rowNum':15,
            'rowList':[15,30,50],
            'viewrecords':True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
        }

And add the following method to the ``MovieController`` class::

    @expose('myapp.templates.widget')
    def grid(self, *args, **kw):
        mw = tw2.core.core.request_local()['middleware']
        mw.controllers.register(GridWidget, 'db_jqgrid')
        return dict(widget=GridWidget, page='movie')

Redirect your browser to http://localhost:8080/movie/grid and you should
see the sortable, searchable jQuery grid.
