tw2.forms with Elixir
=====================

Elixir is a ORM; a library for interfacing with the database. This tutorial shows how to use tw2.forms with Elixir. It builds on standalone.py - TBD


Model
-----

The first step is to define the database tables. We'll use Elixir as our object-relational mapper; this is an active record style ORM that builds on SQLAlchemy. Add the following to ``myapp.py``::

    import elixir as el
    el.metadata.connect('sqlite:///myapp.db')
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

    el.setup_all()

The next step is to actually create the database tables, and some test data. In the python interpreter, issue::

    >>> from myapp2 import *
    >>> el.metadata.create_all()

    >>> jb = People(name='Joe Bloggs')
    >>> jd = People(name='Jane Doe')
    >>> sp = Status(name='Pending')
    >>> sd = Status(name='Dispatched')
    >>> Order(name='Garden furniture', status=sp, customer=jb, assignee=jd)
    >>> Order(name='Barbeque', status=sd, customer=jd, assignee=jb)
    >>> el.session.commit()


Front Page
----------

The front page of the application needs to be a list of orders, so we can update the ``Index`` class as follows::

    class Index(twc.Page):
        class child(twf.GridLayout):
            name = twf.LabelField()
            status = twf.LabelField()
            customer = twf.LabelField()
            assignee = twf.LabelField()

        def fetch_data(self, req):
            self.value = Order.query.all()

With all this done, restart the application, refresh the browser page, and you'll see the list of orders.


Form Editing
------------

Users need to be able to click on an order to get further information. We'll build an inital version of the detail form using ToscaWidgets. Add the following to ``myapp.py``::

    class OrderForm(twf.FormPage):
        title = 'Order'
        class child(twd.CustomisedForm):
            class child(twd.HidingTableLayout):
                id = twf.HiddenField()
                name = twf.TextField()
                status_id = twf.SingleSelectField(options=[str(r) for r in Status.query.all()])
                customer_id = twf.SingleSelectField(options=[str(r) for r in People.query.all()])
                assignee_id = twf.SingleSelectField(options=[str(r) for r in People.query.all()])
                delivery = twf.CheckBox()
                address = twf.TextArea()

        def fetch_data(self, req):
            self.value = Order.query.get(req.GET['id'])

    mw.controllers.register(OrderForm, 'order')

Users will need a link from the front page to the edit page. Update the ``Index`` class and add, at the beginning::

    id = twf.LinkField(link='order?id=$', text='Edit', label=None)

Have a look at this in your browser - you will now be able to navigate from the order list, to the order editing form. To make the form save when you click "submit", add the following to the ``Order`` class::

    @classmethod
    def validated_request(cls, req, data):
        Order.query.get(id).from_dict(data)
        # TBD: redirect

You can now use your browser to edit orders in the system. This arrangement provides the basis for a highly functional system. In particular, validation can easily be added, with the error messages reported in a user-friendly way. It's also easy to adapt this to form a "create new order" function.
