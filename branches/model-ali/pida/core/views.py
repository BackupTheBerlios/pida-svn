

class view_mixin(object):

    __views__ = []

    def init(self):
        self.__views = {}
        self.__viewdefs = {}
        for definition in self.__class__.__views__:
            self.__viewdefs[definition.__name__] = definition

    def create_view(self, viewname, **kw):
        viewdef = self.__viewdefs[viewname]
        view = viewdef.view_type(service=self,
                                 prefix=viewname, **kw)
        self.__views[view.unique_id] = view
        view.view_definition = viewdef
        view.connect('removed', self.__view_closed_base)
        return view

    def show_view(self, unique_id=None, view=None):
        if view is None:
            if unique_id is None:
                raise KeyError('Need either view, or unique_id')
            view = self.__views[unique_id]
        book_name = view.view_definition.book_name
        self.boss.call_command('window', 'append_page',
                                bookname=book_name, view=view)

    def raise_view(self, view):
        self.boss.call_command('window', 'raise_page', view=view)

    def get_view(self, unique_id):
        return self.__views[unique_id]

    def get_first_view(self, viewname):
        for view in self.__views.values():
            if view.view_definition.__name__ == viewname:
                return view
        raise KeyError('No views of that type')

    def view_confirm_close(self, view):
        return True

    def view_confirm_detach(self, view):
        return True

    def close_view(self, view):
        if self.view_confirm_close(view):
            self.boss.call_command('window', 'remove_page', view=view)
            view.emit('removed')

    def __view_closed_base(self, view):
        del self.__views[view.unique_id]
        self.view_closed(view)

    def view_closed(self, view):
        pass

    def detach_view(self, view, detach):
        if detach:
            self.boss.call_command('window', 'remove_page', view=view)
            self.boss.call_command('window', 'append_page',
                                   bookname='ext', view=view)
        else:
            self.boss.call_command('window', 'remove_page', view=view)
            self.show_view(view=view)
            

    def view_detached_base(self, view):
        self.view_detached(self, view)

    def view_detached(self, view):
        pass

# the data views


class DefaultingDict(dict):

    def __getitem__(self, item):
        return self.setdefault(item, set())

from pida.pidagtk.tree import Tree


import gtk

from kiwi.ui.widgets.checkbutton import CheckButton
from kiwi.ui.widgets.filechooser import ProxyFileChooserButton
from kiwi.ui.widgets.fontbutton import ProxyFontButton
from kiwi.ui.widgets.colorbutton import ProxyColorButton
from kiwi.ui.widgets.spinbutton import ProxySpinButton
from kiwi.ui.widgets.entry import Entry
from kiwi.ui.widgets.label import Label, ProxyLabel
from cgi import escape
import os
import gobject
NAME_MU = """%s:"""
DOC_MU = """<small><i>%s</i></small>"""
SECTION_TITLE="<big><b>%s</b></big>"
SECTION_DESCRIPTION="<i>%s</i>"
VC_NAME_MU='<span color="#0000c0"><b>%s</b></span>'
BOLD_MU='<b>%s</b>'
from model import property_evading_setattr

class FormattedLabel(ProxyLabel):
    def __init__(self, format_string):
        super(FormattedLabel, self).__init__()
        self.format_string = format_string
        self.set_property('data-type', str)

    def update(self, data):
        self.set_markup(self.format_string % data)

from model import BaseSingleModelObserver

class WidgetObserver(BaseSingleModelObserver):

    def __init__(self, *args):
        super(WidgetObserver, self).__init__(*args)
        self._widgets = DefaultingDict()
        self._sensitive_widgets = DefaultingDict()

    def add_widget(self, widget, attr, sensitive_attr=None):
        self._widgets[attr].add(widget)
        if sensitive_attr:
            self._sensitive_widgets[sensitive_attr].add(widget)
            val = getattr(self._model, sensitive_attr) or False
            widget.set_sensitive(val)
        widget.set_property('model-attribute', attr)
        widget.connect('content-changed', self.on_changed, attr)

    def add_widget_from_view(self, view, widget_name, attr):
        widget = view.get_widget(name)
        self.add_widget(widget, attr)

    def __model_notify__(self, model, attr, value):
        for widget in self._widgets[attr]:
            widget.update(value)

    def on_changed(self, widget, attr):
        self.update_model(widget.get_property('model-attribute'), widget.read())
        for widget in self._sensitive_widgets[attr]:
            val = getattr(self._model, attr) or False
            widget.set_sensitive(val)

from registry import types

def get_widget_for_type(rtype):
    if rtype is types.boolean:
        return CheckButton()
    elif rtype is types.file:
        w = ProxyFileChooserButton('Select File')
        w.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        return w
    elif rtype in [types.directory]:
        w = ProxyFileChooserButton('Select Directory')
        w.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        return w
    elif rtype is types.font:
        return ProxyFontButton()
    elif rtype is types.color:
        return ProxyColorButton()
    elif rtype is types.integer:
        w = ProxySpinButton()
        return w
    elif rtype.__name__ is 'intrange':
        adjvals = rtype.lower, rtype.upper, rtype.step
        adj = gtk.Adjustment(0, *adjvals)
        w = ProxySpinButton()
        w.set_adjustment(adj)
        return w
    else:
        return Entry(data_type=str)

from model import ModelGroup, Model,  BaseMultiModelObserver

import gobject

class TreeObserver(Tree, BaseMultiModelObserver):

    def __init__(self, model_attributes, current_callback):
        Tree.__init__(self)
        BaseMultiModelObserver.__init__(self, model_attributes)
        self._current_callback = current_callback
        self.connect('clicked', self.cb_clicked)

    def cb_clicked(self, tree, item):
        self._current_callback(item.value)

    def set_current_model(self, item):
        if not self.selected or self.selected.value is not item:
            self.set_selected(hash(item))

    def add_model(self, item):
        key = hash(item)
        super(TreeObserver, self).add_model(item)
        return self.add_item(item, key=key)

    def __model_notify__(self, model, attr, value):
        model.reset_markup()

class PropertyPage(WidgetObserver):

    __model_attributes__ = []

    def __init__(self, *args):
        super(PropertyPage, self).__init__(*args)
        self._pages = {}
        self._lsizer = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        self._nb = gtk.Notebook()

    def set_model(self, model):
        oldmod = dir(self._model)
        super(PropertyPage, self).set_model(model)
        if oldmod == dir(self._model):
            return
        for page in xrange(self._nb.get_n_pages()):
            self._nb.remove_page(page)
        for group, doc, attr_names in model.__model_groups__:
            self.add_page(group, gtk.STOCK_OK, doc, attr_names)
        for attr in model.__model_attrs__:
            widget = get_widget_for_type(attr.rtype)
            self.pack_widget(widget, attr=attr.key,
                             label=attr.label, doc=attr.doc,
                             sensitive_attr=attr.sensitive_attr)
        self._nb.show_all()
        self.set_model(model)


    def get_widget(self):
        return self._nb

    def add_page(self, title, stock_id, description, attrs):
        page = gtk.VBox()
        page.pack_start(self.create_title_label(title,
            description, stock_id), expand=False)
        self._pages[tuple(attrs)] = page
        self._nb.append_page(page,
            tab_label=self.create_tab_label(title, stock_id))

    def pack_widget(self, widget, attr, sensitive_attr=None, label=None,
                    doc=None):
        self.add_widget(widget, attr, sensitive_attr)
        for attrs in self._pages:
            if attr in attrs:
                lw = self.create_labelled_widget(widget, label, doc)
                self._pages[attrs].pack_start(lw, expand=False)

    def create_labelled_widget(self, widget, label, doc):
        if label is None:
            label = widget.get_property('model-attribute')
        if doc is None:
            doc = 'No documentation'
        vb = gtk.VBox()
        vb.set_border_width(6)
        hb = gtk.HBox(spacing=6)
        vb.pack_start(hb)
        hb.set_border_width(0)
        if isinstance(widget, CheckButton):
            widget.set_label(label)
        else:
            l = gtk.Label(label)
            l.set_alignment(0, 0.5)
            hb.pack_start(l, expand=False)
            self._lsizer.add_widget(l)
        hb.pack_start(widget, expand=False)
        vb.pack_start(self.create_doc_label(doc), expand=False)
        return vb

    def create_title_label(self, title, desc, stock_id):
        hb = gtk.HBox(spacing=6)
        i = gtk.Image()
        i.set_from_stock(stock_id, gtk.ICON_SIZE_LARGE_TOOLBAR)
        hb.pack_start(i, expand=False)
        vb=gtk.VBox()
        hb.pack_start(vb)
        l = gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_markup(SECTION_TITLE % escape(title))
        vb.pack_start(l, expand=False)
        l = gtk.Label()
        l.set_alignment(0, 0.5)
        l.set_markup(SECTION_DESCRIPTION % escape(desc))
        vb.pack_start(l, expand=False)
        hb.set_border_width(6)
        return hb

    def create_doc_label(self, doc):
        d = gtk.Label()
        d.set_markup(DOC_MU % escape(doc))
        d.set_alignment(0, 0.5)
        d.set_line_wrap(True)
        return d

    def create_tab_label(self, title, stock_id):
        hb = gtk.HBox()
        i = gtk.Image()
        i.set_from_stock(stock_id, gtk.ICON_SIZE_MENU)
        hb.pack_start(i)
        l = gtk.Label(title)
        hb.pack_start(l)
        hb.show_all()
        return hb


class ProjectDefinition(object):
    __order__ = ['source']

    class source:
        """
        Options relating to source
        """
        __order__ = ['uses', 'directory']
        class uses:
            """
            Whether the project has source code
            """
            rtype = types.boolean
            label = 'Uses Source'
            default = True

        class directory:
            """
            The location of theproject's source directory
            """
            rtype = types.intrange(1, 99, 1)
            label = 'Source Directory'
            default = 25
            sensitive_attr = 'source__uses'

    @staticmethod
    def __markup__(self):
        from cgi import escape
        return escape('%s' % self.source__directory)

class ProjectGroup(ModelGroup):

    __model_attributes__ = None

mg = ProjectGroup()

w = gtk.Window()
b = gtk.HBox()
tv = mg.create_multi_observer(TreeObserver)
tv.set_property('markup-format-string', '%(__model_markup__)s')
tv2 = mg.create_multi_observer(TreeObserver)
tv2.set_property('markup-format-string', '%(__model_markup__)s')
pp = mg.create_single_observer(PropertyPage)
from model import Model
from persistency import IniFileObserver, load_model_from_ini
ini = mg.create_multi_observer(IniFileObserver)
b.pack_start(tv)
b.pack_start(pp.get_widget())
b.pack_start(tv2)
w.add(b)


m1 =  Model(ProjectDefinition)
m2 =  Model(ProjectDefinition)
m3 =  Model(ProjectDefinition)

m4 = load_model_from_ini('/tmp/foo_modelini', ProjectDefinition)

for m in [m1, m2, m3, m4]:
    mg.add_model(m)


mg.set_current(m2)

w.show_all()
gtk.main()



