"""
This app is the end result of the "customising appearance" tutorial
"""
import tw2.core as twc, tw2.forms as twf, os

class Index(twf.FormPage):
    title = 'tw2.forms Customising Appearance'
    resources = [twc.CSSLink(filename='appearance.css')]
    template = 'genshi:%s/appearance.html' % os.getcwd()
    class child(twf.TableForm):
        name = twf.TextField(validator=twc.Required)
        group = twf.SingleSelectField(options=['Red', 'Green', 'Blue'])
        notes = twf.TextArea()
        submit = twf.SubmitButton(value='Go!')

if __name__ == '__main__':
    import wsgiref.simple_server as wrs
    wrs.make_server('', 8000, twc.make_middleware(controller_prefix='/')).serve_forever()
