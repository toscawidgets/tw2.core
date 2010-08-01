"""
A data grid can be achieved using a GridLayout that contains LabelField widgets.
"""
import tw2.core as twc, tw2.forms as twf

class Index(twc.Page):
    title = 'Data Grid'
    class child(twf.GridLayout):
        extra_reps = 0
        id = twf.LinkField(link='detail?id=$', text='View', label=None)
        a = twf.LabelField()
        b = twf.LabelField()

    def fetch_data(self, req):
        self.value = [{'id':1, 'a':'paj','b':'bob'}, {'id':2, 'a':'joe','b':'jill'}]

if __name__ == '__main__':
    import wsgiref.simple_server as wrs
    wrs.make_server('', 8000, twc.make_middleware(controller_prefix='/')).serve_forever()
