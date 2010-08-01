import tw2.core as twc, tw2.forms as twf

import elixir as el
el.metadata.bind = 'sqlite:///elixir.db'
el.options_defaults['shortnames'] = True


class People(el.Entity):
    name = el.Field(el.String(100))
    email = el.Field(el.String(100))
    def __str__(self):
        return self.name

class Status(el.Entity):
    name = el.Field(el.String(100))
    def __str__(self):
        return self.name

class Order(el.Entity):
    name = el.Field(el.String(100))
    status = el.ManyToOne(Status)
    customer = el.ManyToOne(People)
    assignee = el.ManyToOne(People)
    delivery = el.Field(el.Boolean)
    address = el.Field(el.String(200))
    items = el.OneToMany('Item')

class Item(el.Entity):
    order = el.ManyToOne(Order)
    code = el.Field(el.String(50))
    description = el.Field(el.String(200))

el.setup_all()



class Index(twc.Page):
    title = 'Orders'
    class child(twf.GridLayout):
        id = twf.LinkField(link='order?id=$', text='Edit', label=None)
        name = twf.LabelField()
        status = twf.LabelField()
        customer = twf.LabelField()
        assignee = twf.LabelField()

    def fetch_data(self, req):
        self.value = Order.query.all()


class OrderForm(twf.FormPage):
    title = 'Order'
    class child(twf.Form):
        class child(twf.TableLayout):
            id = twf.HiddenField()
            name = twf.TextField()
            status_id = twf.SingleSelectField(options=[str(r) for r in Status.query.all()])
            customer_id = twf.SingleSelectField(options=[str(r) for r in People.query.all()])
            assignee_id = twf.SingleSelectField(options=[str(r) for r in People.query.all()])
            delivery = twf.CheckBox()
            address = twf.TextArea()

    def fetch_data(self, req):
        self.value = Order.query.get(req.GET['id'])


if __name__ == '__main__':
    import wsgiref.simple_server as wrs
    wrs.make_server('', 8000, twc.make_middleware(controller_prefix='/')).serve_forever()
