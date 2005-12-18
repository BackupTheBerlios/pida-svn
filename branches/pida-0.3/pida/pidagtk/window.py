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
import multipaned
import paned
# gtk import(s)
import gtk
import gobject


class pida_v_paned(gtk.VPaned):

    def __init__(self):
        gtk.VPaned.__init__(self)
        
    def on_pane_notify(self, pane, gparamspec):
        # A widget property has changed.  Ignore unless it is 'position'.
        print gparamspec.name
        def clear():
            pane.set_property('position-set', False)
        if gparamspec.name == 'position-set':
            gobject.timeout_add(1000, clear)

class pidawindow(paned.paned_window):

    def __init__(self, manager):
        paned.paned_window.__init__(self)
        self.__manager = manager
        self.__viewbooks = {}
        from pkg_resources import Requirement, resource_filename
        icon_file = resource_filename(Requirement.parse('pida'),
                                      'pida-icon.svg')
        im = gtk.Image()
        im.set_from_file(icon_file)
        self.set_icon(im.get_pixbuf())


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
        #bar = multipaned.multi_paned()
        bar = gtk.VBox()
        bufferlist = self.__manager.buffermanager
        bar.pack_start(bufferlist)
        bar.pack_start(self.__manager.pluginmanager)
        vb = self.__viewbooks['language'] = contentbook.contentbook('Languages')
        bar.pack_start(vb)
        vb.collapse()
        vb = self.__viewbooks['content'] = contentbook.contentbook('Quick View')
        bar.pack_start(vb)
        vb.collapse()
        return bar

    def reset(self):
        """Pack the required components."""
        mainbox = gtk.VBox()
        self.add(mainbox)
        menu = self.__manager.menubar
        topbar = gtk.HBox()
        toolbar = self.__manager.toolbar
        self.__toolarea = gtk.VBox()
        self.top_area.pack_start(self.__toolarea)
        self.__toolarea.pack_start(menu, expand=False)
        self.__toolarea.pack_start(toolbar, expand=True)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        mainbox.pack_start(topbar, expand=False)
        self.__p0 = gtk.HPaned()
        def on_pane_notify(pane, gparamspec):
            # A widget property has changed.  Ignore unless it is 'position'.
            if gparamspec.name == 'position':
                print 'pane position is now', pane.get_property('position')
        self.__p0.connect('notify', on_pane_notify)
        mainbox.pack_start(self.__p0)
        bufferlist = gtk.Label('tb')
        pluginbook = gtk.Label('pluginbook')
        sidebar_orientation_horizontal = False
        sidebar_on_right = False
        

        editor = contentbook.Contentholder(show_tabs=False)
        #ew = pida_v_paned()
        #ew.pack1(editor, resize=True, shrink=True)

        self.__viewbooks['edit'] = editor

        viewbook = contentbook.contentbook('Content')
        #ew.pack2(viewbook, resize=True, shrink=False)

        self.__viewbooks['view'] = viewbook

        #self.__editor_pane = ew
        self.__side_pane = self.__create_sidebar()

        self.set_main_widget(editor)
        self.set_pane_widget(gtk.POS_BOTTOM, viewbook)

        self.set_pane_widget(gtk.POS_LEFT, self.__side_pane)
        self.set_pane_sticky(gtk.POS_LEFT, True)

        #if sidebar_on_right:
        #    self.__p0.pack1(self.__editor_pane)
        #    self.__p0.pack2(self.__side_pane)
        #else:
        #    self.__p0.pack1(self.__side_pane)
        #    self.__p0.pack2(self.__editor_pane)

        self.set_size_request(800, 600)
        #self.__side_pane.set_size_request(300, -1)


    def toggle_book(self, name):
        if name in self.__viewbooks:
            self.__viewbooks[name].toggle()

    def shrink_book(self, name):
        if name in self.__viewbooks:
            self.__viewbooks[name].shrink()


