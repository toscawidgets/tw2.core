Standalone Tutorial
===================

Installing ToscaWidgets 2
-------------------------

First of all, you need Python; version 2.5 is recommended. ToscaWidgets 2 is currently in early development, so take the latest version of each library from the repositories. You need to install Mercurial and issue the following::

    hg clone http://bitbucket.org/paj/tw2core/ tw2.core
    hg clone http://bitbucket.org/paj/tw2devtools/ tw2.devtools
    hg clone http://bitbucket.org/paj/tw2forms/ tw2.forms
    hg clone http://bitbucket.org/paj/tw2dynforms/ tw2.dynforms
    hg clone http://bitbucket.org/paj/tw2.sqla/ tw2.sqla

Then go into each directory in turn and issue::

    python setup.py develop

.. note::
    These instructions will shortly change to using ``easy_install``, when the packages are released on PyPI.
    
This will install the widgets libraries and dependencies. Once this is complete, try running the widget browser to check the install worked. Issue::

    paster tw2.browser
    
And browse to ``http://localhost:8000/``, where you should be able to see the installed widgets.

If you have any problems during install, try asking on the mailing list.


Building a Page
---------------

To get started, we'll build a simple "Hello World" application. First, create ``myapp.py`` with the following::

    import tw2.core as twc
    
    class Index(twc.Page):
        template = 'genshi:./index.html'
    
    twc.dev_server()

Here were are creating a Page widget, called Index, with a template specified. Index is a special name that matches the root URL. We need to create the template, so in the same directory, create ``index.html`` with the following content::

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

This is a Genshi template. This simple example just uses static HTML, but the template system has many other features to explore. Now, start the application::

    myapp.py

And browse to ``http://localhost:8000/`` to check that it's working.

To go beyond simple static HTML, the first step is to have Python code executed when the page is generated. The ``fetch_data`` method is called at this time, and we can override this to hook the event. We will add simple code that reflects the received request. Add the following to `Index`::

    def fetch_data(self, req):
        self.req = str(req)

The ``req`` variable supplied is a WebOb ``Request`` object. To access a URL parameter, use ``req.GET['myparam']``. In this example, we simply use the string representation of the request.

And in ``index.html``, change the ``<p>Hello World!</p>`` line to::

    <pre>$w.req</pre>
    
The ``$w`` variable refers to the Python widget object that called the template.

Restart the application and refresh your browser to see this.


Building a Form
---------------

We'll now create a simple form. In this example we're going to create a movie database. First, add to the top of ``myapp.py``::

    import tw2.forms as twf

Now, add to this file, before ``twc.dev_server()``::

    class Movie(twf.FormPage):
        title = 'Movie'
        class child(twf.TableForm):
            title = twf.TextField(validator=twc.Required)
            director = twf.TextField()
            genre = twf.CheckBoxList(options=['Action', 'Comedy', 'Romance', 'Sci-fi'])
            class cast(twf.GridLayout):
                extra_reps = 5
                character = twf.TextField()
                actor = twf.TextField()

Before we explain this code, browse to ``http://localhost:8000/movie`` to see how the form looks. Have a go an entering values and submitting; notice the difference when you specify a title compared to not.

The `FormPage` widget adds functionality beyond `Page` in that it handles POST requests and redisplays the form on validation failures. The `TableForm` widget displays the form, including the submit button, and does the table layout. The form fields are specified in a fairly self-explanatory manner, noting that validation is specified for `title`. Here, `GridLayout` is used as a kind of sub-form, which allows multiple cast members to be specified.

The form does not look particularly appealing. To try to improve this, lets add some CSS. We'll start with something simple; create ``myapp.css`` with the following::

    TBD

use CSS to make it a bit nicer
use required class




Connecting to a Database
------------------------

The next step is to save movies to a database. To do this, we'll use SQLAlchemy and Elixir to define a database model. Create ``model.py`` with the following::

    import elixir as el, tw2.sqla as tws
    el.session = tws.transactional_session()
    el.metadata = el.sqlalchemy.MetaData('sqlite:///myapp.db')

This is code is required to set up the database connection. It will use an SQLite database, ``myapp.db`` in the current directory. Now, add the code to define our tables::

    class Movie(el.Entity):
        title = el.Field(el.String)
        director = el.Field(el.String)
        genre = el.ManyToMany('Genre')
        case = el.OneToMany('Cast')
    
    class Genre(el.Entity):
        name = el.Field(el.String)
        def __unicode__(self):
            return self.name
    
    class Cast(el.Entity):
        movie = el.ManyToOne(Movie)
        character = el.Field(el.String)
        actor = el.Field(el.String)    

    el.setup_all()

This defines three tables - Movie, Genre and Cast, with relations between them. To learn more about the Elixir syntax, read the Elixir tutorial. The next step is to create our database. Issue::

    python
    >>> import model as db
    >>> db.el.create_all()

Make form use db



Next Steps
----------

List front page
Genres from database
GrowingGrid
