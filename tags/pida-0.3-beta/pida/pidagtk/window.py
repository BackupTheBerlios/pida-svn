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

# gtk import(s)
import gtk

# pidagtk import(s)
import paned
import expander
import contentbook


class pidawindow(gtk.Window):
    """The Pida main window"""

    def __init__(self, manager):
        super(gtk.Window, self).__init__()
        self.set_title('PIDA loves you')
        self.__manager = manager
        self.__viewbooks = {}
        from pkg_resources import Requirement, resource_filename
        icon_file = resource_filename(Requirement.parse('pida'),
                                      'pida-icon.png')
        im = gtk.Image()
        im.set_from_file(icon_file)
        self.set_icon(im.get_pixbuf())

    def append_page(self, bookname, page):
        if bookname in self.__viewbooks:
            self.__viewbooks[bookname].append_page(page)
            self.__viewbooks[bookname].show_all()
            if bookname == 'language':
                if not self.__manager.opt('panes',
                    'automatically_expand_language_bar'):
                    return True
            try:
                pos = self._get_book_position(self.__viewbooks[bookname])
                self.set_pane_sticky(pos, True)
            except AttributeError, e:
                pass
            return True
        else:
            return False

    def remove_pages(self, bookname):
        if bookname in self.__viewbooks:
            book = self.__viewbooks[bookname]
            book.detach_pages()

    def _create_sidebar(self, bufferview, pluginview):
        sidebar_horiz = self.__manager.opt('layout',
                                           'vertical_sidebar_split')
        if sidebar_horiz:
            box = gtk.HPaned()
        else:
            box = gtk.VPaned()
        bar = gtk.VBox()
        box.pack1(bar, resize=True)
        bufs = expander.expander()
        bufs.set_body_widget(bufferview)
        l = gtk.Label('Buffer list')
        l.set_alignment(0, 0.5)
        bufs.set_label_widget(l)
        bufs.expand()
        bar.pack_start(bufs, expand=True)
        bar.pack_start(pluginview)
        bar2 = gtk.VBox()
        box.pack2(bar2, resize=True)
        vb = self.__viewbooks['language'] = contentbook.contentbook('Languages')
        bar2.pack_start(vb)
        vb.collapse()
        vb = self.__viewbooks['content'] = contentbook.contentbook('Quick View')
        bar2.pack_start(vb)
        vb.collapse()
        return box

    def pack(self, menubar, toolbar, bufferview, pluginview):
        self.__mainbox = gtk.VBox()
        self.add(self.__mainbox)
        self._pack_topbar(menubar, toolbar)
        self._pack_panes(bufferview, pluginview)

    def _pack_topbar(self, menubar, toolbar):
        self.__toolarea = gtk.VBox()
        self.__mainbox.pack_start(self.__toolarea, expand=False)
        self.__toolarea.pack_start(menubar, expand=False)
        self.__toolarea.pack_start(toolbar, expand=False)
        toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
        self.__menubar = menubar
        self.__toolbar = toolbar

    def _pack_panes(self, bufferview, pluginview):
        editor = contentbook.Contentholder(show_tabs=False)
        self.__viewbooks['edit'] = editor
        self.set_main_widget(editor)
        self._create_paneholder('view', gtk.POS_BOTTOM)
        sidebar_on_right = self.__manager.opt('layout', 'sidebar_on_right')
        if sidebar_on_right:
            panepos = gtk.POS_RIGHT
            langpos = gtk.POS_LEFT
        else:
            panepos = gtk.POS_LEFT
            langpos = gtk.POS_RIGHT
        #self._create_paneholder('language', langpos)
        sidebar = self._create_sidebar(bufferview, pluginview)
        self.set_pane_widget(panepos, sidebar)
        self.set_pane_sticky(panepos, True)
        extb = self.__viewbooks['ext'] = external_book()
        extb.window.set_transient_for(self)

    def _pack_panes(self, bufferview, pluginview):
        p0 = gtk.HPaned()
        self.__mainbox.pack_start(p0)
        sidebar_width = self.__manager.opt('layout', 'sidebar_width')
        sidebar_on_right = self.__manager.opt('layout', 'sidebar_on_right')
        sidebar = self._create_sidebar(bufferview, pluginview)
        p1 = gtk.VPaned()
        if sidebar_on_right:
            side_func = p0.pack2
            main_func = p0.pack1
            main_pos = 800 - sidebar_width
        else:
            side_func = p0.pack1
            main_func = p0.pack2
            main_pos = sidebar_width
        side_func(sidebar, resize=False)
        main_func(p1, resize=True)
        p0.set_position(main_pos)
        editor = contentbook.Contentholder(show_tabs=False)
        self.__viewbooks['edit'] = editor
        p1.pack1(editor, resize=True)
        viewbook = contentbook.Contentholder()
        self.__viewbooks['view'] = viewbook
        p1.pack2(viewbook, resize=False)
        extb = self.__viewbooks['ext'] = external_book()
        p1.set_position(430)
        self.resize(800, 600)

    def _create_paneholder(self, name, position):
        viewbook = contentbook.Contentholder()
        self.__viewbooks[name] = viewbook
        self.set_pane_widget(position, viewbook)
        viewbook.connect('empty', self.cb_empty, name)

    def _get_book_position(self, book):
        return book.position

    def cb_empty(self, book, name):
        pos = self._get_book_position(book)
        self.set_pane_sticky(pos, False)

    def toggle_book(self, name):
       if name in self.__viewbooks:
            self.__viewbooks[name].toggle()

    def shrink_book(self, name):
        if name in self.__viewbooks:
            self.__viewbooks[name].shrink()


class external_window(gtk.Window):

    def __init__(self, *args):
        super(external_window, self).__init__()
        self.__book = contentbook.Contentholder()
        self.__book.notebook.set_show_tabs(False)
        self.add(self.__book)
        self.connect('destroy', self.on_window__destroy)
        self.resize(600, 480)
        self.set_position(gtk.WIN_POS_CENTER)
        self.__book.connect('empty', self.cb_empty)

    def cb_empty(self, holder):
        self.destroy()

    def append_page(self, *args):
        self.__book.append_page(*args)
        self.show_all()
        self.present()

    def on_window__destroy(self, window):
        self.hide()
        self.remove(self.__book)
        self.__book.remove_pages()
        return True

    def get_window(self):
        return self.__window
    window = property(get_window)


class external_book(object):

    def append_page(self, page):
        ext = external_window()
        ext.append_page(page)

    def show_all(self):
        pass


