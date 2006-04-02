

import gtk


import attrtypes as types
from model import Model, ModelGroup
from views import TreeObserver, PropertyPage
from persistency import IniFileObserver, load_model_from_ini

from exampleschema import AddressDefinition

# Creates a model class
Address = Model.__model_from_definition__(AddressDefinition)


class ProjectDefinition(object):
    __order__ = ['general', 'source']

    class general:
        """General options relating to the project"""
        __order__ = ['name', 'filename']
        label = 'General'
        stock_id = gtk.STOCK_PREFERENCES

        class name:
            """The name you would like to refer to the project as"""
            label = 'Project Name'
            rtype = types.string
            default = 'unnamed'

        class filename:
            """The project file location."""
            label = 'Project file'
            rtype = types.file
            default = ''

    class source:
        """Options relating to source code for the project"""
        label = 'Source'
        stock_id = gtk.STOCK_NEW
        __order__ = ['uses', 'directory', 'uses_vc',
                     'vc_name']
        class uses:
            """Whether the project has source code"""
            rtype = types.boolean
            label = 'Has Source Code'
            default = True

        class directory:
            """Select a source directory for the project"""
            rtype = types.directory
            label = 'Source Directory'
            default = '/'
            sensitive_attr = 'source__uses'

        class uses_vc:
            """Whether the project uses version control"""
            rtype = types.boolean
            label = 'Uses Version Control'
            default = True
            sensitive_attr = 'source__uses'

        class vc_name:
            """The version control system"""
            rtype = types.readonly
            label = 'System'
            sensitive_attr = 'source__uses_vc'
            dependents = ['source__directory']

            def fget(self):
                from pida.utils.vc import Vc
                if self.source__uses and self.source__uses_vc:
                    vc = Vc(self.source__directory)
                    if vc.NAME != 'Null':
                        return vc.NAME
                return 'None'

    def __markup__(self):
        from cgi import escape
        mu = '<b>%s</b>' % escape(self.general__name)
        if self.source__uses:
            mu = ('%s (<span color="#0000c0">%s</span>)\n%s'
                    % (mu, escape(self.source__vc_name),
                           escape(self.source__directory)))
        return mu

Project = Model.__model_from_definition__(ProjectDefinition)

if __name__ == '__main__':

    mg = ModelGroup()
    tv = mg.create_multi_observer(TreeObserver)
    pp = mg.create_single_observer(PropertyPage)
    ini = mg.create_multi_observer(IniFileObserver)

    for n in ['Tom', 'Dick', 'Harry']:
        m = Project()
        m = load_model_from_ini('/tmp/foo_model%s2' % n, m)
        m.general__name = n
        mg.add_model(m)

    m = Project()
    load_model_from_ini('/home/ali/tmp/food', m)
    mg.add_model(m)

    # pack the tree and the property page
    b = gtk.HPaned()
    b.pack1(tv)
    b.pack2(pp)
    b.set_position(200)

    # put them in a window for good measure
    w = gtk.Window()
    w.connect('delete-event', lambda w, e: gtk.main_quit())
    w.add(b)
    w.resize(600, 400)
    w.show_all()

    gtk.main() # give life

