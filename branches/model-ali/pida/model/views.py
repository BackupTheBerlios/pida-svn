

from cgi import escape

import gtk
from kiwi.ui.widgets.entry import ProxyEntry
from kiwi.ui.widgets.label import ProxyLabel
from kiwi.ui.widgets.combo import ProxyComboBox
from kiwi.ui.widgets.spinbutton import ProxySpinButton
from kiwi.ui.widgets.fontbutton import ProxyFontButton
from kiwi.ui.widgets.checkbutton import ProxyCheckButton
from kiwi.ui.widgets.colorbutton import ProxyColorButton
from kiwi.ui.widgets.filechooser import ProxyFileChooserButton

import attrtypes as types
from pida.pidagtk.tree import Tree
from model import BaseMultiModelObserver, BaseSingleModelObserver


class DefaultingDict(dict):

    def __getitem__(self, item):
        return self.setdefault(item, set())


class FormattedLabel(ProxyLabel):
    def __init__(self, format_string):
        super(FormattedLabel, self).__init__()
        self.format_string = format_string
        self.set_property('data-type', str)
        self.set_alignment(0, 0.5)

    def update(self, data):
        self.set_markup(self.format_string % data)


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

    def __model_notify__(self, model, attr, value):
        for widget in self._widgets[attr]:
            widget.update(value)

    def on_changed(self, widget, attr):
        self.update_model(widget.get_property('model-attribute'), widget.read())
        for widget in self._sensitive_widgets[attr]:
            val = getattr(self._model, attr) or False
            widget.set_sensitive(val)


def get_widget_for_type(rtype):
    if rtype is types.boolean:
        return ProxyCheckButton()
    elif rtype is types.file:
        w = ProxyFileChooserButton('Select File')
        w.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        return w
    elif rtype in [types.directory]:
        w = ProxyFileChooserButton(title='Select Directory')
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
    elif rtype is types.readonly:
        return FormattedLabel(VC_NAME_MU)
    elif rtype.__name__ is 'stringlist':
        w = ProxyComboBox()
        w.set_property('data-type', str)
        w.prefill(rtype.choices)
        return w
    else:
        w = ProxyEntry(data_type=str)
        w.set_width_chars(18)
        return w

class TreeObserver(Tree, BaseMultiModelObserver):

    def __init__(self, model_attributes, current_callback):
        Tree.__init__(self)
        self.set_property('markup-format-string', '%(__model_markup__)s')
        BaseMultiModelObserver.__init__(self, model_attributes,
                                        current_callback)
        self.connect('clicked', self.cb_clicked)

    def cb_clicked(self, tree, item):
        self.current_callback(item.value)

    def set_model(self, item):
        if not self.selected or self.selected.value is not item:
            self.set_selected(hash(item))

    def add_model(self, item):
        key = hash(item)
        super(TreeObserver, self).add_model(item)
        return self.add_item(item, key=key)

    def __model_notify__(self, model, attr, value):
        model.reset_markup()

class PropertyPage(gtk.VBox, WidgetObserver):

    __model_attributes__ = []

    def __init__(self, *args):
        gtk.VBox.__init__(self)
        WidgetObserver.__init__(self, *args)
        self._pages = {}
        self._nb = gtk.Notebook()
        self._tips = gtk.Tooltips()
        self.pack_start(self._nb)

    def set_model(self, model):
        oldmod = dir(self._model)
        super(PropertyPage, self).set_model(model)
        if oldmod == dir(self._model):
            return
        for page in xrange(self._nb.get_n_pages()):
            self._nb.remove_page(page)
        for group, doc, label, stock_id, attr_names in model.__model_groups__:
            self.add_page(group, label, stock_id, doc, attr_names)
        for attr in model.__model_attrs__:
            widget = get_widget_for_type(attr.rtype)
            self.pack_widget(widget, attr=attr.key,
                             label=attr.label, doc=attr.doc,
                             sensitive_attr=attr.sensitive_attr)
        self._nb.show_all()
        self.set_model(model)

    def get_widget(self):
        return self._nb

    def add_page(self, group, title, stock_id, description, attrs):
        holder = gtk.ScrolledWindow()
        holder.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        page = gtk.VBox()
        page.set_border_width(12)
        holder.add_with_viewport(page)
        page.pack_start(self.create_title_label(title,
            description, stock_id), expand=False)
        lsizer = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        vsizer = gtk.SizeGroup(gtk.SIZE_GROUP_VERTICAL)
        self._pages[tuple(attrs)] = page, lsizer, vsizer
        self._nb.append_page(holder,
            tab_label=self.create_tab_label(title, stock_id))

    def pack_widget(self, widget, attr, sensitive_attr=None, label=None,
                    doc=None):
        self.add_widget(widget, attr, sensitive_attr)
        for attrs in self._pages:
            if attr in attrs:
                page, sizer, vsizer = self._pages[attrs]
                lw = self.create_labelled_widget(widget, sizer, vsizer, label,
                                                 doc)
                page.pack_start(lw, expand=False)

    def create_labelled_widget(self, widget, sizer, vsizer, label, doc):
        if label is None:
            label = widget.get_property('model-attribute')
        if doc is None:
            doc = 'No documentation'
        vb = gtk.EventBox()
        vb.set_border_width(6)
        hb = gtk.HBox(spacing=12)
        vb.add(hb)
        hb.set_border_width(0)
        if 0:#isinstance(widget, ProxyCheckButton):
            widget.set_label(label)
            hb.pack_start(gtk.Label())
            ltext = ' '
        else:
            ltext = label
        l = gtk.Label(ltext)
        l.set_alignment(0, 0.5)
        hb.pack_start(l, expand=False)
        sizer.add_widget(l)
        al = gtk.Alignment(0, 0.5, 1, 1)
        al.add(widget)
        hb.pack_start(al, expand=True)
        #vb.pack_start(self.create_doc_label(doc), expand=False)
        self._tips.set_tip(vb, doc)
        vsizer.add_widget(vb)
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


# markup definitions
DOC_MU = """<small><i>%s</i></small>"""
SECTION_TITLE="<big><b>%s</b></big>"
SECTION_DESCRIPTION="<i>%s</i>"
VC_NAME_MU='<b>%s</b>'




