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

import toolbar
class IContentPage:

    pass

class ContentView(gtk.VBox):

    __gsignals__ = {'action' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,))}

    def __init__(self):
        gtk.VBox.__init__(self)
        self.__toolbar = toolbar.Toolbar()
        self.pack_start(self.__toolbar, expand=False, fill=False)
        self.__toolbar.connect('clicked', self.cb_toolbar_clicked)

    def add_button(self, name, icon):
        button = self.__toolbar.add_button(name, icon)
        self.show_all()

    def add_menuitem(self):
        pass

    def cb_toolbar_clicked(self, toolbar, name):
        self.emit('action', name)
    

class ContentBook(ContentView):
    
    def __init__(self):
        ContentView.__init__(self)
        self.__notebook = gtk.Notebook()
        self.pack_start(self.__notebook)
        self.__notebook.set_tab_pos(gtk.POS_TOP)
        self.__notebook.set_scrollable(True)
        self.__notebook.set_property('show-border', False)
        self.__notebook.set_property('tab-border', 2)
        self.__notebook.set_property('enable-popup', True)
    
    def append_page(self, contentview):
        self.__notebook.append_page(contentview)
        self.__notebook.show_all()
