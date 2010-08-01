import elixir as el, tw2.sqla as tws
el.session = tws.transactional_session()
el.metadata = el.sqlalchemy.MetaData('sqlite:///myapp.db')


class Movie(el.Entity):
    title = el.Field(el.String)
    director = el.Field(el.String)
    genre = el.ManyToMany('Genre')
    cast = el.OneToMany('Cast')

class Genre(el.Entity):
    name = el.Field(el.String)
    def __unicode__(self):
        return self.name

class Cast(el.Entity):
    movie = el.ManyToOne(Movie)
    character = el.Field(el.String)
    actor = el.Field(el.String)    


el.setup_all()
