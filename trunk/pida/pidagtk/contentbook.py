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

class Contentholder(gtk.VBox):

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

    def __init_notebook(self, show_tabs):
        self.__notebook = gtk.Notebook()
        self.pack_start(self.__notebook)
        self.__notebook.set_tab_pos(gtk.POS_BOTTOM)
        self.__notebook.set_scrollable(True)
        self.__notebook.set_show_border(False)
        self.__notebook.set_show_tabs(show_tabs)
        self.__notebook.set_property('tab-border', 2)
        self.__notebook.set_property('homogeneous', True)
        self.__notebook.set_property('enable-popup', True)
        self.__notebook.set_show_border(False)
        self.__notebook.popup_disable()

    def append_page(self, contentview):
        tab_label = gtk.EventBox()
        tab_label.add(contentview.icon)
        tab_label.show_all()
        tooltiptext = contentview.LONG_TITLE
        if not tooltiptext:
            tooltiptext = contentview.SHORT_TITLE
        if not tooltiptext:
            tooltiptext = 'No tooltip set for %s' % contentview
        icons.tips.set_tip(tab_label, tooltiptext)
        self.__notebook.append_page(contentview, tab_label=tab_label)
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

    def __get_notebook(self):
        return self.__notebook
    notebook = property(__get_notebook)

    def cb_view_short_title_changed(self, view):
        self.__list_widget.set_title(view, view.short_title)

    def cb_list_clicked(self, listholder, unique_id):
        contentview = self.__views[unique_id]
        contentview.raise_page()

gobject.type_register(Contentholder)

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

gobject.type_register(content_list)

class ContentholderList(content_list):

    def init(self):
        self.__views = {}
        self.__buttons = {}
        self.__currentuid = None

    def append_page(self, contentview):
        #label = widgets.hyperlink('', icon=contentview.icon)
        label = contentview.icon
        group = None
        if len(self.__buttons):
            group = self.__buttons.values()[0]
        button = gtk.RadioToolButton(group)
        #button.set_icon_widget(label)
        #button.set_mode(False)
        button.set_active(True)
        button.set_icon_widget(label)
        button.connect('toggled', self.cb_button_clicked, contentview.unique_id)
        self.__views[contentview.unique_id] = label
        self.__buttons[contentview.unique_id] = button
        self.pack_start(button, expand=False)
        #self.set_title(contentview)

    def remove_page(self, contentview):
        button = self.__buttons[contentview.unique_id]
        self.remove(button)
        del self.__views[contentview.unique_id]
        del self.__buttons[contentview.unique_id]

    def set_page(self, contentview):
        self.__set_selected_uid(contentview.unique_id)

    def set_title(self, contentview):
        label = self.__views[contentview.unique_id]
        label.set_text(contentview.short_title)

    def __set_selected_uid(self, uid):
        for closeuid in self.__views:
            if uid == closeuid:
                self.__currentuid = closeuid
                button = self.__buttons[closeuid]
                #self.__views[closeuid].set_selected()
                #button.set_active(True)
            else:
                pass
                #self.__views[closeuid].set_unselected()
            

    def cb_button_clicked(self, button, unique_id):
        if unique_id != self.__currentuid:
            self.__set_selected_uid(unique_id)
            self.emit('clicked', unique_id)
            return True

class contentbook(expander.expander):

    def __init__(self, name):
        self.__name = name
        expander.expander.__init__(self)

    def populate(self):
        self.__contentholderlist = ContentholderList()
        #self.set_label_widget(self.__contentholderlist)
        lab = gtk.Label(self.__name)
        lab.set_alignment(0, 0.5)
        self.set_label_widget(lab)
        self.__contentholder = Contentholder(self.__contentholderlist)
        self.__contentholder.connect('empty', self.cb_empty)
        self.set_body_widget(self.__contentholder)
        self.set_sensitive(False)

    def append_page(self, contentview):
        self.expand()
        self.set_sensitive(True)
        return self.__contentholder.append_page(contentview)

    def detach_pages(self):
        self.__contentholder.detach_pages()
        

    def set_page(self, contentview):
        return self.__contentholder.set_page(contentview)

    def cb_empty(self, contentholder):
        self.collapse()
        self.set_sensitive(False)


