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
sys.path.insert(2, '/home/ali/working/pida/pida/branches/pida-ali/')

import registrywidgets

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
    name_label.set_markup(SECTION_TITLE % optiongroup.name)
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
        name_label = gtk.Label(group.name)
        notebook.append_page(page, tab_label=name_label)
        widgets.extend(wids)
    if len(reg) == 1:
        notebook.set_show_tabs(False)
    return notebook, widgets

class config_view(contentview.content_view):

    def init(self):
        self.__registries = {}
        self.__pages = {}
        self.__widgets = {}
        self.__init_widgets()

    def __init_widgets(self):
        pane = gtk.HPaned()
        self.widget.pack_start(pane)
        self.__list = tree.Tree()
        pane.pack1(self.__list)
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
        but = gtk.Button(stock=gtk.STOCK_APPLY)
        box.pack_start(but)
        but = gtk.Button(stock=gtk.STOCK_SAVE)
        box.pack_start(but)
        but = gtk.Button(stock=gtk.STOCK_CANCEL)
        box.pack_start(but)

    def __build_list(self):
        for name in self.__registries:
            class di(object):
                key = name
            self.__list.add_item(di(), key=name)

    def __build_page(self, pagename):
        if pagename in self.__pages:
            page = self.__pages[pagename]
            self.__set_current_page(page)
        elif pagename in self.__registries:
            reg = self.__registries[pagename]
            page, wids = create_notebook_from_registry(reg, pagename)
            self.__pages[pagename] = page
            for names, wid in wids:
                self.__widgets[names] = wid
            self.__notebook.append_page(page)
            page.show_all()
            self.__set_current_page(page)

    def __set_current_page(self, page):
        pagenum = self.__notebook.page_num(page)
        self.__notebook.set_current_page(pagenum)

    def set_registries(self, registries):
        for name, reg in registries:
            if len(reg):
                self.__registries[name] = reg
        self.__build_list()

    def cb_list_clicked(self, listview, item):
        self.__build_page(item.key)



class ListedTab(gtk.VBox):

    __gsignals__ = {'closed' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'applied' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'reverted' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'new-item' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
    
    TREE = tree.Tree
    TREE_ITEM = RegistryTreeItem

    def __init__(self, registry):
        gtk.VBox.__init__(self)
        self.__registry = registry
        self.__populate()
        self.__reset()

    def __populate(self):
        mainbox = gtk.HBox()
        self.add(mainbox)
        leftbox = gtk.VBox()
        mainbox.pack_start(leftbox, expand=False)
        leftbox.set_size_request(220, -1)
        self.__sectionview = self.TREE()
        leftbox.pack_start(self.__sectionview)
        self.__sectionview.connect("clicked", self.cb_section_clicked)
        self.__sectionview.connect('new-item', self.cb_new_item)
        self.__sectionview.connect('edit-item', self.cb_edit_item)
        self.__sectionview.connect('delete-item', self.cb_delete_item)
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
        self.__revert_button = icons.icons.get_text_button('undo', 'Revert')
        cb.pack_start(self.__revert_button, expand=False)
        self.__revert_button.connect('clicked', self.cb_revert)
        self.__applybutton = icons.icons.get_text_button('apply', 'Apply')
        cb.pack_start(self.__applybutton, expand=False)
        self.__applybutton.connect('clicked', self.cb_apply)
        self.__savebutton = icons.icons.get_text_button('save', 'Save')
        cb.pack_start(self.__savebutton, expand=False)
        self.__savebutton.connect('clicked', self.cb_save)


    def __build_sectionlist(self):
        self.__sectionview.clear()
        first = True
        for group in self.__registry.iter_groups():#_alphabetically():
            treeitem = self.TREE_ITEM(group.get_name(), group)
            self.__sectionview.add_item(treeitem)
            if first:
                first = False
                self.__sectionview.set_selected(group.get_name())

    def __reset(self):
        self.__pages = {}
        self.__widgets = []
        def remove(page):
            self.__notebook.remove(page)
        self.__notebook.foreach(remove)
        self.__build_sectionlist()

    def reset(self):
        current_name = self.__sectionview.get_selected_key()
        self.__reset()
        self.__sectionview.set_selected(current_name)

    def create_page(self, section_name):


        if not section_name in self.__pages:
            size_group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
            group = self.__registry.get_group(section_name)
            b = gtk.VBox()
            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            sw.add_with_viewport(b)
            name_label = gtk.Label()
            name_label.set_markup(SECTION_NAME_MU % section_name)
            name_label.set_justify(gtk.JUSTIFY_LEFT)
            b.pack_start(name_label, expand=False)
            doc_label = gtk.Label()
            doc_label.set_markup(SECTION_DOC_MU % group.doc)
            b.pack_start(doc_label, expand=False)
            b.pack_start(gtk.HSeparator(), expand=False, padding=4)
            self.__pages[section_name] = sw
            for opt in group.iter_alphabetically():
                w = opt.DISPLAY_WIDGET(opt)
                b.pack_start(w.win, expand=False, padding=6)
                size_group.add_widget(w.widget)
                w.load()
                self.__widgets.append(w)
            sw.show_all()
        return self.__pages[section_name]
            
    def display_page(self, section_name):
        if section_name != self.__sectionview.get_selected_key():
            self.__sectionview.set_selected(section_name)
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

    def cb_revert(self, button):
        self.emit('reverted')

    def cb_save(self, button):
        self.__apply()
        self.__registry.save()

    def cb_apply(self, button):
        self.__apply()

    def cb_section_clicked(self, tree, item):
        self.display_page(item.value.name)

    def cb_delete_item(self, tab):
        self.__registry.delete_group(self.__sectionview.get_selected_key())
        self.reset()

    def cb_edit_item(self, tab):
        pass

    def new(self, name):
        self.emit('new-item', name)

    def cb_new_item(self, tab):
        def new(name):
            self.emit('new-item', name)
        self.__sectionview.question(self.new, 'foo')

gobject.type_register(ListedTab)

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
        if hasattr(obj, "get_children"):
            for child in obj.get_children():
                tree(child, ind + 2)
    gtk.main()
