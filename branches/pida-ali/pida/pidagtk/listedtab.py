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

import sys
sys.path.insert(2, '/home/ali/working/pida/pida/branches/pida-ali/')

class EditTree(tree.Tree):
        EDIT_BUTTONS = True

class RegistryTreeItem(tree.TreeItem):
    def __get_markup(self):
        return self.value.name
    markup = property(__get_markup)

class ListedTab(gtk.VBox):

    __gsignals__ = {'clicked' : (
                    gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,
                    (gobject.TYPE_PYOBJECT,))}
    
    TREE = tree.Tree
    TREE_ITEM = RegistryTreeItem

    def __init__(self, registry):
        gtk.VBox.__init__(self)
        self.__registry = registry
        self.__pages = {}
        self.__populate()
        self.__build_sectionlist()

    def __populate(self):
        mainbox = gtk.HBox()
        self.add(mainbox)

        leftbox = gtk.VBox()
        mainbox.pack_start(leftbox, expand=False)
        leftbox.set_size_request(120, -1)

        self.__sectionview = self.TREE()
        leftbox.pack_start(self.__sectionview)
        self.__sectionview.connect("clicked", self.cb_section_clicked)

        rightbox = gtk.VBox()
        mainbox.pack_start(rightbox)

        self.__notebook = gtk.Notebook()
        rightbox.pack_start(self.__notebook)

        attrbox = gtk.VBox()
        rightbox.pack_start(attrbox)


        hbox = gtk.HBox()
        attrbox.pack_start(hbox, expand=False, padding=4)
        namelabel = gtk.Label('name')
        hbox.pack_start(namelabel, expand=False, padding=4)
        self.nameentry = gtk.Entry()
        hbox.pack_start(self.nameentry)

        # Button Bar
        cb = gtk.HBox()
        rightbox.pack_start(cb, expand=False, padding=2)
        
        # separator
        sep = gtk.HSeparator()
        cb.pack_start(sep)
        
        # reset button
        revert_b = gtk.Button(stock=gtk.STOCK_REVERT_TO_SAVED)
        cb.pack_start(revert_b, expand=False)
        revert_b.connect('clicked', self.cb_revert)

        # cancel button
        delete_b = gtk.Button(stock=gtk.STOCK_DELETE)
        cb.pack_start(delete_b, expand=False)
        delete_b.connect('clicked', self.cb_delete)
        
        # apply button
        new_b = gtk.Button(stock=gtk.STOCK_NEW)
        cb.pack_start(new_b, expand=False)
        new_b.connect('clicked', self.cb_new)
        
        # save button
        save_b = gtk.Button(stock=gtk.STOCK_SAVE)
        cb.pack_start(save_b, expand=False)
        save_b.connect('clicked', self.cb_save)

    def __build_sectionlist(self):
        for group in self.__registry.iter_groups():
            treeitem = self.TREE_ITEM(group.get_name(), group)
            self.__sectionview.add_item(treeitem)
    
    def new(self):
        pass

    def create_page(self, section_name):
        if not section_name in self.__pages:
            group = self.__registry.get_group(section_name)
            b = gtk.VBox()
            b.pack_start(gtk.Label(section_name))
            b.pack_start(gtk.Label(group.doc))
            self.__pages[section_name] = b
            for opt in group:
                w = opt.DISPLAY_WIDGET(opt)
                b.pack_start(w.win)
                w.load()
            b.show_all()
        return self.__pages[section_name]
            
    def display_page(self, section_name):
        page = self.create_page(section_name)
        if self.__notebook.page_num(page) == -1:
            self.__notebook.append_page(page)
        page_num = self.__notebook.page_num(page)
        self.__notebook.set_current_page(page_num)
            
    def projects_changed(self):
        self.project_registry.save()
        self.projects.populate(self.project_registry)
        self.do_evt('projectschanged')

    def pages(self):
        for page_num in xrange(self.__notebook.get_n_pages()):
            yield self.__notebook.get_nth_page(page_num)
            
    def cb_project_select(self, *args):
        projname = self.projects.selected(0)
        self.display(projname)
         
    def cb_new(self, *args):
        self.new()

    def cb_revert(self, *args):
        self.project_registry.load()
        self.projects_changed()

    def cb_save(self, *args):
        name = self.nameentry.get_text()
        if name:
            kw = {}
            for attrname in self.attribute_widgets:
                kw[attrname] = self.attribute_widgets[attrname].get_text()
            self.project_registry.set_project(name, **kw)
            self.projects_changed()

    def cb_delete(self, *args):
        projname = self.projects.selected(0)
        self.project_registry.delete(projname)
        self.projects_changed()
        self.projects.view.set_cursor(self.projects.model[0].path)

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
