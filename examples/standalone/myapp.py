import tw2.core as twc
import tw2.forms as twf
import tw2.sqla as tws
import model as db

class Index(tws.DbListPage):
    entity = db.Movie
    title = 'Movies'
    newlink = twf.LinkField(link='movie', text='New', value=1)
    class child(twf.GridLayout):
        id = twf.LinkField(link='movie?id=$', text='Edit')
        title = twf.LabelField()

class Movie(tws.DbFormPage):
    entity = db.Movie
    title = 'Movie'
    redirect = '/'
    resources = [twc.CSSLink(filename='myapp.css')]
    class child(twf.TableForm):
        title = twf.TextField(validator=twc.Required)
        director = twf.TextField()
        genre = tws.DbCheckBoxList(entity=db.Genre)
        class cast(twf.GridLayout):
            extra_reps = 5
            character = twf.TextField()
            actor = twf.TextField()

twc.dev_server(repoze_tm=True)
