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

import tree
import icons
import gtk
import gobject
import registrywidgets
import contentview

from kiwi.utils import gsignal, gproperty

class data_view(contentview.content_view):

    def init(self):
        self.__list = data_list(self.service)
        self.__list.connect('new-item', self.cb_list_newitem)
        self.__list.connect('applied', self.cb_list_applied)
        self.widget.pack_start(self.__list)
        self.__init_buttons()
        
    def __init_buttons(self):
        holder = gtk.Alignment()
        self.widget.pack_start(holder, expand=False, padding=5)
        box = gtk.HButtonBox()
        holder.add(box)
        save_but = gtk.Button(stock=gtk.STOCK_SAVE)
        box.pack_start(save_but)
        def save_clicked(button):
            self.__list.save_record()
        save_but.connect('clicked', save_clicked)
        def close_clicked(button):
            pass

    def set_database(self, dataname, database, schema):
        self.__dataname = dataname
        self.__database = database
        self.__list.set_database(database, schema)

    def cb_list_newitem(self, list, name):
        self.service.cb_data_view_newitem(self.__dataname, name)

    def cb_list_applied(self, list):
        self.service.cb_data_view_applied(self.__dataname)

class editable_tree(tree.Tree):

    EDIT_BUTTONS = True
    EDIT_BOX = True


class data_list(gtk.HPaned):

    __gsignals__ = {'closed' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'applied' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'reverted' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, ()),
                    'new-item' : (gobject.SIGNAL_RUN_LAST,
                                 gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}


    def __init__(self, service):
        gtk.HPaned.__init__(self)
        self.__service = service
        self.__init_widgets()
        
    def set_database(self, database, schema):
        self.__database = database
        self.__schema = schema
        self.__build_list(self.__datalist)
        self.__build_page()

    def view_record(self, key):
        self.__list.set_selected(key)

    def save_record(self):
        self.__save_page()

    def __init_widgets(self):
        self.__datalist = editable_tree()
        self.__datalist.set_size_request(150, -1)
        self.__datalist.connect('clicked', self.cb_list_clicked)
        self.__datalist.connect('new-item', self.cb_list_newitem)
        self.pack1(self.__datalist)

    def __build_page(self):
        page = gtk.VBox()
        self.pack2(page)
        title_box = gtk.HBox()
        self.__title_label = gtk.Label()
        title_box.pack_start(self.__title_label)
        page.pack_start(title_box, expand=False)
        page.pack_start(gtk.HSeparator(), expand=False)
        self.__build_datawidgets(page)
        
    def __build_datawidgets(self, page):
        self.__datawidgets = {}
        size = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        lsize = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        #size.set_orientation(gtk.SIZE_GROUP_HORIZONTAL)
        for name, rtype, default, doc in self.__schema:
            option = rtype(name, doc, default)
            widget_type = registrywidgets.get_widget(rtype)
            widget = widget_type(option)
            page.pack_start(widget.win, expand=False)
            size.add_widget(widget.widget)
            lsize.add_widget(widget.name_l)
            self.__datawidgets[name] = widget

    def __build_list(self, datalist):
        datalist.clear()
        for key in self.__database:
            class list_item(object):
                def __init__(self, key):
                    self.key = key
            datalist.add_item(list_item(key))

    def __view_page(self, key):
        record = self.__database[key]
        for field_name, widget in self.__datawidgets.iteritems():
            value = getattr(record, field_name)
            widget.option.value = value
            widget.load()

    def __save_page(self):
        key = self.__datalist.get_selected_key()
        record = self.__database[key]
        for field_name, widget in self.__datawidgets.iteritems():
            widget.save()
            setattr(record, field_name, widget.option.value)
        self.__database.save()
        self.emit('applied')
        
    def cb_list_clicked(self, tree, item):
        self.__view_page(item.key)
            
    def cb_list_newitem(self, tree):
        def new(name):
            self.emit('new-item', name)
            self.__build_list(self.__datalist)
        self.__datalist.question(new, 'foo')
    


