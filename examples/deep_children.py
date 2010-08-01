import tw2.core as twc, tw2.forms as twf

opts = ['Red', 'Yellow', 'Green', 'Blue']

class Index(twf.FormPage):
    title = 'tw2.forms Deep Children'
    class child(twf.Form):
        class child(twc.CompoundWidget):
            class noname(twf.TableFieldSet):
                id = None
                legend = 'Contact Info'
                name = twf.TextField()
                email = twf.TextField(validator=twc.EmailValidator())
            class noname2(twf.TableFieldSet):
                id = None
                legend = 'Work Info'
                job_title = twf.TextField(validator=twc.Required)
                location = twf.TextField()

if __name__ == "__main__":
    import wsgiref.simple_server as wrs
    wrs.make_server('', 8000, twc.make_middleware(controller_prefix='/')).serve_forever()
