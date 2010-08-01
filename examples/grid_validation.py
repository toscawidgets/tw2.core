import tw2.core as twc, tw2.forms as twf

class Index(twf.FormPage):
    title = 'GridLayout Validation'
    class child(twf.Form):
        class child(twf.GridLayout):
            repetitions = 5
            name = twf.TextField(validator=twc.Required)
            email = twf.TextField(validator=twc.EmailValidator())

if __name__ == '__main__':
    import wsgiref.simple_server as wrs
    wrs.make_server('', 8000, twc.make_middleware(controller_prefix='/')).serve_forever()
