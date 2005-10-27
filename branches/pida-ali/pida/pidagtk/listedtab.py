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

import sys
sys.path.insert(2, '/home/ali/working/pida/pida/branches/pida-ali/')

class EditTree(tree.Tree):
        EDIT_BUTTONS = True

class RegistryTreeItem(tree.TreeItem):
    def __get_markup(self):
        return self.value.name
    markup = property(__get_markup)


SECTION_NAME_MU = """<span weight="bold" size="small">%s</span>"""
SECTION_DOC_MU = """<span size="small">%s</span>"""

class ListedTab(gtk.VBox):

    __gsignals__ = {'closed' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'applied' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ())}
    
    TREE = tree.Tree
    TREE_ITEM = RegistryTreeItem

    def __init__(self, registry):
        gtk.VBox.__init__(self)
        self.__registry = registry
        self.__pages = {}
        self.__widgets = []
        self.__populate()
        self.__build_sectionlist()

    def __populate(self):
        mainbox = gtk.HBox()
        self.add(mainbox)
        leftbox = gtk.VBox()
        mainbox.pack_start(leftbox, expand=False)
        leftbox.set_size_request(220, -1)
        self.__sectionview = self.TREE()
        leftbox.pack_start(self.__sectionview)
        self.__sectionview.connect("clicked", self.cb_section_clicked)
        rightbox = gtk.VBox()
        mainbox.pack_start(rightbox)
        self.__notebook = gtk.Notebook()
        rightbox.pack_start(self.__notebook)
        self.__notebook.set_show_tabs(False)
        self.__notebook.set_show_border(False)
        cb = gtk.HBox()
        rightbox.pack_start(cb, expand=False, padding=2)
        sep = gtk.HSeparator()
        cb.pack_start(sep)
        self.__cancelbutton = icons.icons.get_text_button('close', 'Close')
        cb.pack_start(self.__cancelbutton, expand=False)
        self.__cancelbutton.connect('clicked', self.cb_close)
        self.__applybutton = icons.icons.get_text_button('apply', 'Apply')
        cb.pack_start(self.__applybutton, expand=False)
        self.__applybutton.connect('clicked', self.cb_apply)
        self.__savebutton = icons.icons.get_text_button('save', 'Save')
        cb.pack_start(self.__savebutton, expand=False)
        self.__savebutton.connect('clicked', self.cb_save)

    def __build_sectionlist(self):
        first = True
        for group in self.__registry.iter_groups_alphabetically():
            treeitem = self.TREE_ITEM(group.get_name(), group)
            self.__sectionview.add_item(treeitem)
            if first:
                first = False
                self.__sectionview.set_selected(group.get_name())
        

    def create_page(self, section_name):
        if not section_name in self.__pages:
            size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
            group = self.__registry.get_group(section_name)
            b = gtk.VBox()
            name_label = gtk.Label()
            name_label.set_markup(SECTION_NAME_MU % section_name)
            name_label.set_justify(gtk.JUSTIFY_LEFT)
            b.pack_start(name_label, expand=False)
            doc_label = gtk.Label()
            doc_label.set_markup(SECTION_DOC_MU % group.doc)
            b.pack_start(doc_label, expand=False)
            b.pack_start(gtk.HSeparator(), expand=False, padding=4)
            self.__pages[section_name] = b
            for opt in group.iter_alphabetically():
                w = opt.DISPLAY_WIDGET(opt)
                b.pack_start(w.win, expand=False, padding=6)
                size_group.add_widget(w.widget)
                w.load()
                self.__widgets.append(w)
            b.show_all()
        return self.__pages[section_name]
            
    def display_page(self, section_name):
        page = self.create_page(section_name)
        if self.__notebook.page_num(page) == -1:
            self.__notebook.append_page(page)
        page_num = self.__notebook.page_num(page)
        self.__notebook.set_current_page(page_num)
            
    def pages(self):
        for page_num in xrange(self.__notebook.get_n_pages()):
            yield self.__notebook.get_nth_page(page_num)
            
    def __apply(self):
        for widget in self.__widgets:
            widget.save()
        self.emit("applied")

    def cb_close(self, button):
        self.emit("closed")

    def cb_save(self, button):
        self.__apply()
        self.__registry.save()

    def cb_apply(self, button):
        self.__apply()

    def cb_section_clicked(self, tree, item):
        self.display_page(item.value.name)

class NewItemTab(ListedTab):
    TREE = EditTree

if __name__ == '__main__':
    import pida.core.registry as registry
    r = registry.Registry('/home/ali/tmp/reg')
    g = r.add_group('first', 'The docs for first group')
    e = g.add('blahA', 'docs for blahA', 1, registry.Boolean)
    e.setdefault()
    e = g.add('blahB', 'docs for blahB', 0, registry.Boolean)
    e.setdefault()
    g = r.add_group('sec', 'The docs for sec group')
    e = g.add('blahA', 'docs for blahA', 2, registry.Boolean)
    e.setdefault()
    e = g.add('blahB', 'docs for blahB', 0, registry.Boolean)
    e.setdefault()

    w = gtk.Window()
    t = ListedTab(r)
    w.add(t)
    w.show_all()

    def tree(obj, ind):
        print ind * " ", obj
        if hasattr(obj, "get_children"):
            for child in obj.get_children():
                tree(child, ind + 2)
    gtk.main()
