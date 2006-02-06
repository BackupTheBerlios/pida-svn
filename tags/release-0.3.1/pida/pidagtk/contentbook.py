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
import icons

class ContentBook(gtk.VBox):

    __gsignals__ = {'empty' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

    def __init__(self, listwidget=None, show_tabs=True):
        gtk.VBox.__init__(self)
        self.__init_notebook(show_tabs)
        self.__list_widget = listwidget
        if listwidget is not None:
            listwidget.connect('clicked', self.cb_list_clicked)
        self.__views = {}
        self.__saved = None

    def __init_notebook(self, show_tabs):
        self.__notebook = gtk.Notebook()
        self.__notebook.show()
        self.pack_start(self.__notebook)
        self.__notebook.set_scrollable(True)
        self.__notebook.set_show_border(False)
        self.__notebook.set_show_tabs(show_tabs)
        self.__notebook.set_property('tab-border', 2)
        self.__notebook.set_property('homogeneous', False)
        self.__notebook.set_property('enable-popup', True)
        self.__notebook.set_show_border(False)
        self.set_tab_position(gtk.POS_RIGHT)
        self.__notebook.popup_disable()

    def set_tab_position(self, position):
        self.__notebook.set_tab_pos(position)

    def append_page(self, contentview):
        tab_label = gtk.EventBox()
        tab_label.show()
        l = gtk.Label(contentview.short_title)
        pos = self.notebook.get_tab_pos()
        if pos in [gtk.POS_LEFT, gtk.POS_RIGHT]:
            box = gtk.VBox(spacing=4)
            l.set_angle(270)
        else:
            box = gtk.HBox(spacing=4)
        box.pack_start(contentview.icon, expand=False)
        eb = contentview.create_tooltip_box()
        eb.add(l)
        box.pack_start(eb, expand=False)
        tab_label.add(box)
        tab_label.show_all()
        
        # Set the tooltip text
        tooltiptext = contentview.long_title
        if not tooltiptext:
            tooltiptext = contentview.short_title
        if not tooltiptext:
            tooltiptext = 'No tooltip set for %s' % contentview
        icons.tips.set_tip(tab_label, tooltiptext)
        
        # Add the content view
        contentview.show()
        self.__notebook.append_page(contentview, tab_label=tab_label)
        self.__views[contentview.unique_id] = contentview
        contentview.holder = self
        contentview.connect('short-title-changed',
                            self.cb_view_short_title_changed)
                            
        if self.__list_widget is not None:
            self.__list_widget.append_page(contentview)

        self.set_page(contentview)

    def set_page(self, contentview=None):
        if contentview is not None:
            pagenum = self.__notebook.page_num(contentview)
            self.__notebook.set_current_page(pagenum)
        else:
            pagenum = self.__notebook.get_current_page()
            contentview = self.__notebook.get_nth_page(pagenum)
        if self.__list_widget is not None:
            self.__list_widget.set_page(contentview)
        contentview.grab_focus()
        contentview.emit('raised')

    def remove_page(self, contentview):
        self.detach_page(contentview)
        contentview.emit('removed')

    def remove_pages(self):
        for uid in self.__views.keys():
            self.remove_page(self.__views[uid])

    def detach_pages(self):
        for uid in self.__views.keys():
            self.detach_page(self.__views[uid])

    def detach_page(self, contentview):
        pagenum = self.__notebook.page_num(contentview)
        self.__notebook.remove_page(pagenum)
        if self.__list_widget is not None:
            self.__list_widget.remove_page(contentview)
        del self.__views[contentview.unique_id]
        if len(self.__views) == 0:
            self.emit('empty')

    def save_state(self):
        self.__saved = self.__notebook.get_current_page()

    def load_state(self):
        if self.__saved is not None:
            self.__notebook.set_current_page(self.__saved)

    def next_page(self):
        if (self.notebook.get_current_page() ==
                self.notebook.get_n_pages() - 1):
            self.notebook.set_current_page(0)
        else:
            self.notebook.next_page()
        self.set_page()

    def previous_page(self):
        if self.notebook.get_current_page() == 0:
            self.notebook.set_current_page(-1)
        else:
            self.notebook.prev_page()
        self.set_page()

    def __get_notebook(self):
        return self.__notebook
    notebook = property(__get_notebook)

    def cb_view_short_title_changed(self, view):
        self.__list_widget.set_title(view, view.short_title)

    def cb_list_clicked(self, listholder, unique_id):
        contentview = self.__views[unique_id]
        contentview.raise_page()

gobject.type_register(ContentBook)


