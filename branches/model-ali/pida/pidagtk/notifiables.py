# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import gtk

from kiwi.ui.widgets.checkbutton import CheckButton
from kiwi.ui.widgets.filechooser import ProxyFileChooserButton
from kiwi.ui.widgets.entry import Entry
from kiwi.ui.widgets.label import Label, ProxyLabel
from cgi import escape
import gobject
NAME_MU = """%s:"""
DOC_MU = """<small><i>%s</i></small>"""
SECTION_TITLE="<big><b>%s</b></big>"
SECTION_DESCRIPTION="<i>%s</i>"
VC_NAME_MU='<span color="#0000c0"><b>%s</b></span>'
BOLD_MU='<b>%s</b>'
from pida.utils.vc import Vc


class FormattedLabel(ProxyLabel):
    def __init__(self, format_string):
        super(FormattedLabel, self).__init__()
        self.format_string = format_string
        self.set_property('data-type', str)

    def update(self, data):
        self.set_markup(self.format_string % data)

class PropertyPage(Widgetnotifiable):

    def __init__(self):
        super(PropertyPage, self).__init__()
        self._pages = {}
        self._lsizer = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        self._nb = gtk.Notebook()

    def get_widget(self):
        return self._nb

    def add_page(self, title, stock_id, description, attrs):
        page = gtk.VBox()
        page.pack_start(self.create_title_label(title,
            description, stock_id), expand=False)
        self._pages[attrs] = page
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

