import elixir, tw2.sqla
elixir.session = tw2.sqla.transactional_session()
elixir.metadata = elixir.sqlalchemy.MetaData('sqlite:///myapp.db')


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


elixir.setup_all()
