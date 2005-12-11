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
import expander
import widgets

class Contentholder(gtk.VBox):

    __gsignals__ = {'empty' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

    def __init__(self, listwidget=None):
        gtk.VBox.__init__(self)
        self.__init_notebook()
        self.__list_widget = listwidget
        if listwidget is not None:
            listwidget.connect('clicked', self.cb_list_clicked)
        self.__views = {}

    def __init_notebook(self):
        self.__notebook = gtk.Notebook()
        self.pack_start(self.__notebook)
        self.__notebook.set_tab_pos(gtk.POS_TOP)
        self.__notebook.set_scrollable(True)
        self.__notebook.set_show_border(False)
        #self.__notebook.set_show_tabs(False)
        self.__notebook.set_property('tab-border', 2)
        self.__notebook.set_property('homogeneous', True)
        self.__notebook.set_property('enable-popup', True)
        self.__notebook.set_show_border(False)

    def append_page(self, contentview):
        self.__notebook.append_page(contentview)
        self.__views[contentview.unique_id] = contentview
        contentview.holder = self
        contentview.connect('short-title-changed',
                            self.cb_view_short_title_changed)
        if self.__list_widget is not None:
            self.__list_widget.append_page(contentview)
        self.__notebook.show_all()
        self.set_page(contentview)

    def set_page(self, contentview):
        pagenum = self.__notebook.page_num(contentview)
        self.__notebook.set_current_page(pagenum)
        if self.__list_widget is not None:
            self.__list_widget.set_page(contentview)
        contentview.emit('raised')

    def remove_page(self, contentview):
        self.detach_page(contentview)
        contentview.emit('removed')

    def detach_pages(self):
        for uid in self.__views.keys():
            self.detach_page(self.__views[uid])

    def detach_page(self, contentview):
        pagenum = self.__notebook.page_num(contentview)
        self.__notebook.remove_page(pagenum)
        if self.__list_widget is not None:
            self.__list_widget.remove_page(contentview)
        del self.__views[contentview.unique_id]
        if len(self.__views) == None:
            self.emit('empty')

    def __get_notebook(self):
        return self.__notebook
    notebook = property(__get_notebook)

    def cb_view_short_title_changed(self, view):
        self.__list_widget.set_title(view, view.short_title)

    def cb_list_clicked(self, listholder, unique_id):
        contentview = self.__views[unique_id]
        contentview.raise_page()

class content_list(gtk.HBox):

    __gsignals__ = {'clicked' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,))}

    def __init__(self):
        gtk.HBox.__init__(self)
        self.init()

    def init(self):
        pass

class ContentholderList(content_list):

    def init(self):
        self.__views = {}
        self.__buttons = {}

    def append_page(self, contentview):
        label = widgets.hyperlink('', icon=contentview.icon)
        button = gtk.ToolButton()
        button.set_icon_widget(label)
        
        button.connect('clicked', self.cb_button_clicked, contentview.unique_id)
        self.__views[contentview.unique_id] = label
        self.__buttons[contentview.unique_id] = button
        self.pack_start(button)
        self.set_title(contentview)

    def remove_page(self, contentview):
        button = self.__buttons[contentview.unique_id]
        self.remove(button)
        button.destroy()

    def set_page(self, contentview):
        self.__set_selected_uid(contentview.unique_id)

    def set_title(self, contentview):
        label = self.__views[contentview.unique_id]
        label.set_text(contentview.short_title)

    def __set_selected_uid(self, uid):
        for closeuid in self.__views:
            if uid == closeuid:
                self.__views[closeuid].set_selected()
            else:
                self.__views[closeuid].set_unselected()
            

    def cb_button_clicked(self, button, unique_id):
        self.__set_selected_uid(unique_id)
        self.emit('clicked', unique_id)

class contentbook(expander.expander):

    def populate(self):
        contentholderlist = ContentholderList()
        self.set_label_widget(contentholderlist)
        self.__contentholder = Contentholder(contentholderlist)
        self.set_body_widget(self.__contentholder)

    def append_page(self, contentview):
        self.expand()
        return self.__contentholder.append_page(contentview)

    def detach_pages(self):
        self.__contentholder.detach_pages()
        

    def set_page(self, contentview):
        return self.__contentholder.set_page(contentview)
