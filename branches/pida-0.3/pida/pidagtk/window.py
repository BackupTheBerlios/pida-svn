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

# pidagtk imports
import toolbar
import expander
import contentbook
import contentview

# gtk import(s)
import gtk

class pidawindow(gtk.Window):

    def __init__(self, manager):
        gtk.Window.__init__(self)
        self.__manager = manager
        self.__viewbooks = {}


    def append_page(self, bookname, page):
        if bookname in self.__viewbooks:
            self.__viewbooks[bookname].append_page(page)
            self.__viewbooks[bookname].show_all()
            return True
        else:
            return False

    def remove_pages(self, bookname):
        if bookname in self.__viewbooks:
            book = self.__viewbooks[bookname]
            book.detach_pages()

    def __create_sidebar(self):
        bar = gtk.VBox()
        bufferlist = self.__manager.buffermanager
        bar.pack_start(bufferlist)
        bar.pack_start(self.__manager.pluginmanager)
        for name in ['language', 'content']:
            vb = self.__viewbooks[name] = contentbook.contentbook()
            bar.pack_start(vb)
        return bar


    def reset(self):
        """Pack the required components."""
        mainbox = gtk.VBox()
        self.add(mainbox)
        menu = self.__manager.menubar
        mainbox.pack_start(menu, expand=False)
        topbar = gtk.HBox()
        toolbar = self.__manager.toolbar
        self.__toolarea = gtk.VBox()
        topbar.pack_start(self.__toolarea)
        self.__toolarea.pack_start(toolbar, expand=True)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        mainbox.pack_start(topbar, expand=False)
        self.__p0 = gtk.HPaned()
        mainbox.pack_start(self.__p0)
        bufferlist = gtk.Label('tb')
        pluginbook = gtk.Label('pluginbook')
        sidebar_orientation_horizontal = False
        sidebar_on_right = False
        

        editor = contentbook.Contentholder()
        ew = gtk.VPaned()
        ew.pack1(editor, resize=True, shrink=True)

        self.__viewbooks['edit'] = editor

        viewbook = contentbook.contentbook()
        vb = gtk.VBox()
        vb.pack_start(viewbook)
        ew.pack2(vb, resize=True, shrink=False)

        self.__viewbooks['view'] = viewbook

        self.__editor_pane = ew
        self.__side_pane = self.__create_sidebar()

        if sidebar_on_right:
            self.__p0.pack1(self.__editor_pane)
            self.__p0.pack2(self.__side_pane)
        else:
            self.__p0.pack1(self.__side_pane)
            self.__p0.pack2(self.__editor_pane)

        self.set_size_request(800, 600)
        self.__side_pane.set_size_request(300, -1)


    def toggle_book(self, name):
        if name in self.__viewbooks:
            self.__viewbooks[name].toggle()

    def shrink_book(self, name):
        if name in self.__viewbooks:
            self.__viewbooks[name].shrink()


