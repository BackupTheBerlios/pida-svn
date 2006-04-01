

import gtk


import attrtypes as types
from model import Model, ModelGroup
from views import TreeObserver, PropertyPage
from persistency import IniFileObserver, load_model_from_ini


class AddressDefinition(object):

    __order__ = ['general', 'email']

    class general:
        """General information."""
        label = 'General Information'
        stock_id = gtk.STOCK_PREFERENCES
        __order__ = ['name', 'knows_age', 'age']
        class name:
            """Person's name"""
            label = 'Name'
            rtype = types.string
            default = 'unnamed'
        class knows_age:
            """Whether you know the person's age"""
            label = 'Age known?'
            rtype = types.boolean
            default = False
        class age:
            """The age of the person"""
            label = 'Age'
            rtype = types.intrange(0, 110, 1)
            default = 35
            sensitive_attr = 'general__knows_age'

    class email:
        """Email addresses for the person"""
        label = 'Email Addresses'
        stock_id = gtk.STOCK_NEW
        __order__ = ['home', 'work', 'extra']

        class home:
            """Home email address"""
            label = 'Home Email'
            rtype = types.string
            default = ''

        class work:
            """Work email address"""
            label = 'Work Email'
            rtype = types.readonly
            dependents = ['email__home']

            def fget(self):
                return self.email__home

        class extra:
            """Extra email address"""
            label = 'Extra Email'
            rtype = types.stringlist('11', '22', '33')
            default = '11'

    def __markup__(self):
        mu = self.general__name
        if self.general__knows_age:
            mu += "\n<small>[ %s ]</small>" % self.general__age
        if self.email__home:
            mu += "\n<small>[ %s ]</small>" % self.email__home
        mu += "\n<small>[ %s ]</small>" % self.email__extra
        return mu

# Creates a model class
Address = Model.__model_from_definition__(AddressDefinition)

if __name__ == '__main__':

    mg = ModelGroup()
    tv = mg.create_multi_observer(TreeObserver)
    pp = mg.create_single_observer(PropertyPage)
    ini = mg.create_multi_observer(IniFileObserver)

    for n in ['Tom', 'Dick', 'Harry']:
        m = Address()
        m = load_model_from_ini('/tmp/foo_model%s2' % n, m)
        m.general__name = n
        mg.add_model(m)

    # pack the tree and the property page
    b = gtk.HPaned()
    b.pack1(tv)
    b.pack2(pp)

    # put them in a window for good measure
    w = gtk.Window()
    w.connect('delete-event', lambda w, e: gtk.main_quit())
    w.add(b)
    w.show_all()

    
    gtk.main() # give life

