# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com

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
import gobject
import tree
import toolbar
import icons
import contentview
import sys

import registrywidgets

from pida.utils.kiwiutils import gsignal

class EditTree(tree.Tree):
        EDIT_BUTTONS = True

class RegistryTreeItem(tree.TreeItem):
    def __get_markup(self):
        return self.value.name
    markup = property(__get_markup)


SECTION_NAME_MU = """<span weight="bold">%s</span>"""
SECTION_DOC_MU = """<span>%s</span>"""
NAME_MU = """%s:"""
DOC_MU = """<small><i>%s</i></small>"""
PARENT_TITLE="<big><b>%s</b></big>"
SECTION_TITLE="<big>%s</big>"
SECTION_TAB="%s"
SECTION_DESCRIPTION="<big>%s</big>"

def create_page_from_optiongroup(optiongroup, parentname):
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

    vbox = gtk.VBox(spacing=12)
    vbox.set_border_width(12)
    vbox.show()
    sw.add_with_viewport(vbox)

    name_label = gtk.Label()
    name_label.set_markup(PARENT_TITLE % parentname)
    name_label.set_justify(gtk.JUSTIFY_LEFT)
    name_label.set_alignment(0, 0.5)
    vbox.pack_start(name_label, expand=False)
       
    name_label = gtk.Label()
    name_label.set_markup(SECTION_TITLE %
        ' '.join(optiongroup.name.split('_')).capitalize())
    name_label.set_justify(gtk.JUSTIFY_LEFT)
    name_label.set_alignment(0, 0.5)
    vbox.pack_start(name_label, expand=False)

    hbox = gtk.HBox(spacing=0)
    vbox.pack_start(hbox)
    
    space = gtk.Label("    ")
    space.show()
    hbox.pack_start(space, expand=False)
    hbox.show()
        
    vbox = gtk.VBox(spacing=12)
    hbox.pack_start(vbox, expand=False)
        
    size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
    widgets = []
    for option in optiongroup:
        widget_type = registrywidgets.get_widget(option.__class__)
        widget_holder = widget_type(option)
        widget_holder.load()
        widget_holder.get_widget().show()
        size_group.add_widget(widget_holder.get_name_label())
        vbox.pack_start(widget_holder, expand=False)
        widgets.append(((optiongroup.name, option.name), widget_holder))
    sw.show_all()
    return sw, widgets

def create_notebook_from_registry(reg, regname):
    notebook = gtk.Notebook()
    widgets = []
    for group in reg:
        page, wids = create_page_from_optiongroup(group, regname)
        name_label = gtk.Label()
        name_label.set_markup(SECTION_TAB %
        ' '.join(group.name.split('_')).capitalize())
        notebook.append_page(page, tab_label=name_label)
        widgets.extend(wids)
    if len(reg) == 1:
        notebook.set_show_tabs(False)
    return notebook, widgets

class config_tree(tree.Tree):

    SORT_LIST = ['markup']

class config_view(contentview.content_view):

    gsignal('data-changed')

    has_apply_button = False

    def init(self):
        self.__registries = {}
        self.__pages = {}
        self.__widgets = {}
        self.__init_widgets()
        self.__current_page_name = None

    def __init_widgets(self):
        pane = gtk.HPaned()
        self.widget.pack_start(pane)
        self.__list = config_tree()
        self.__list.set_property('markup-format-string', '%(markup)s')
        pane.pack1(self.__list)
        self.__list.set_size_request(200, -1)
        self.__list.connect('clicked', self.cb_list_clicked)
        self.__notebook = gtk.Notebook()
        pane.pack2(self.__notebook)
        self.__notebook.set_show_tabs(False)
        self.__notebook.set_show_border(False)
        self.__init_buttons()
        
    def __init_buttons(self):
        holder = gtk.Alignment(1, 0.5)
        holder.set_border_width(6)
        self.widget.pack_start(holder, expand=False, padding=5)
        box = gtk.HButtonBox()
        holder.add(box)
        but = gtk.Button(stock=gtk.STOCK_UNDO)
        box.pack_start(but)
        but.connect('clicked', self.cb_undo_clicked)
        but = gtk.Button(stock=gtk.STOCK_APPLY)
        if self.has_apply_button:
            box.pack_start(but)
        but.connect('clicked', self.cb_apply_clicked)
        but = gtk.Button(stock=gtk.STOCK_SAVE)
        box.pack_start(but)
        but.connect('clicked', self.cb_save_clicked)
        but = gtk.Button(stock=gtk.STOCK_CANCEL)
        box.pack_start(but)
        but.connect('clicked', self.cb_cancel_clicked)

    def __build_list(self):
        for name in self.__registries:
            class di(object):
                markup = self.service.boss.get_service_displayname(name)
                if not markup:
                    markup = name
                key = name
            self.__list.add_item(di(), key=name)

    def __build_page(self, pagename):
        if pagename in self.__pages:
            page = self.__pages[pagename]
            self.__set_current_page(page, pagename)
        elif pagename in self.__registries:
            reg = self.__registries[pagename]
            displayname = self.service.boss.get_service_displayname(pagename)
            if not displayname:
                displayname = pagename.capitalize()
            page, wids = create_notebook_from_registry(reg, displayname)
            self.__pages[pagename] = page
            for names, wid in wids:
                self.__widgets[names] = wid
            self.__notebook.append_page(page)
            page.show_all()
            self.__set_current_page(page, pagename)

    def __set_current_page(self, page, pagename):
        self.__current_page_name = pagename
        pagenum = self.__notebook.page_num(page)
        self.__notebook.set_current_page(pagenum)

    def __apply(self):
        for group, name in self.__widgets:
            self.__widgets[(group, name)].save()
        
    def __save(self):
        for name, registry in self.__registries.iteritems():
            registry.save()
        self.emit('data-changed')

    def __reset(self):
        pagename = self.__current_page_name
        print pagename
        for i in xrange(self.__notebook.get_n_pages()):
            self.__notebook.remove_page(i)
        self.__pages = {}
        self.__widgets = {}
        self.set_registries([(name, self.__registries[name])
                             for name in self.__registries])
        self.__list.set_selected(pagename)

    def set_registries(self, registries):
        self.__list.clear()
        first = None
        for name, reg in registries:
            if len(reg):
                if not first:
                    first = name
                self.__registries[name] = reg
        self.__build_list()
        if first is not None:
            self.__list.set_selected(first)

    def cb_list_clicked(self, listview, item):
        self.__build_page(item.key)

    def cb_undo_clicked(self, button):
        self.__reset()

    def cb_apply_clicked(self, button):
        self.__apply()

    def cb_save_clicked(self, button):
        self.__apply()
        self.__save()
        self.close()

    def cb_cancel_clicked(self, button):
        self.close()

    def show_page(self, pagename):
        self.__list.set_selected(pagename)

gobject.type_register(config_view)
