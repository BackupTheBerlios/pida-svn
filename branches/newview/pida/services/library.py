# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Ali Afshar aafshar@gmail.com

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

import os
import gzip
import tempfile
import threading

import xml.sax
import xml.dom.minidom as minidom
xml.sax.handler.feature_external_pes = False

import gtk
import gobject

import pida.utils.gforklet as gforklet
import pida.core.service as service
import pida.core.actions as actions
import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree

defs = service.definitions
types = service.types


class lib_list(tree.Tree):

    SORT_LIST = ['title']


class bookmark_view(contentview.content_view):

    ICON_NAME = 'library'
    LONG_TITLE = 'Documentation Library'
    SHORT_TITLE = 'Docs'

    HAS_CONTROL_BOX = True
    HAS_CLOSE_BUTTON = True

    def init(self):
        pane = gtk.Notebook()
        self.widget.pack_start(pane)
        pane.set_tab_pos(gtk.POS_TOP)
        self.__list = lib_list()
        label = gtk.Label('Books')
        #label.set_angle(90)
        pane.append_page(self.__list, tab_label=label)
        self.__list.connect('clicked', self.cb_booklist_clicked)
        self.__list.connect('double-clicked', self.cb_contents_clicked)
        self.__list.set_property('markup_format_string',
                                 '%(title)s')
        self.__contents = tree.Tree()
        label = gtk.Label('Contents')
        #label.set_angle(90)
        pane.append_page(self.__contents, tab_label=label)
        self.__contents.set_property('markup_format_string',
                                 '%(name)s')
        self.__contents.connect('double-clicked', self.cb_contents_clicked)
        self.long_title = 'Loading books...'
        self.paned = pane

    def book_found(self, book):
        gobject.idle_add(self.__add_list_item, book)

    def __add_list_item(self, item):
        self.__list.add_item(item)
        return False

    def books_done(self):
        self.long_title = 'Documentation library'

    def set_contents(self, book):
        self.__contents.clear()
        for item in book.subs:
            self._add_item(item)

    def _add_item(self, item, parent=None):
        niter = self.__contents.add_item(item, parent=parent)
        for child in item.subs:
            try:
                self._add_item(child, niter)
            except KeyError:
                pass
        
    def cb_booklist_clicked(self, treeview, item):
        if item.value.bookmarks is None:
            item.value.load()
        self.set_contents(item.value.bookmarks)
        self.paned.set_current_page(1)

    def cb_contents_clicked(self, treeview, item):
        book = item.value
        if book.path:
            self.service.boss.call_command('webbrowse', 'browse',
                                           url=book.path)
        else:
            self.service.log.info('Bad document book "%s"', book.name)
        

class document_library(service.service):

    display_name = 'Documentation Library'

    class Library(defs.View):
        view_type = bookmark_view
        book_name = 'plugin'

    class book_locations(defs.optiongroup):
        """Locations of books in the file system."""
        class use_gzipped_book_files(defs.option):
            """Whether to use devhelp.gz format books."""
            rtype = types.boolean
            default = True

    def init(self):
        self.get_action().set_active(False)
        self.books = []
        self.fetch()
        self.__view = None

    def fetch_thread(self):
        t = threading.Thread(target=self.fetch_books)
        t.start()

    def fetch_forklet(self):
        gforklet.fork_generator(self.fetch_books(), [],
                                self.single_view.book_found)

    def fetch(self):
        self.fetch_thread()

    def fetch_books(self):
        pida_directory = os.path.join(self.boss.pida_home, 'library')
        dirs = [pida_directory, '/usr/share/gtk-doc/html',
                                '/usr/share/devhelp/books',
                                os.path.expanduser('~/.devhelp/books')]
        use_gzip = self.opt('book_locations', 'use_gzipped_book_files')
        def _fetch(directory):
            if os.path.exists(directory):
                for name in os.listdir(directory):
                    path = os.path.join(directory, name)
                    if os.path.exists(path):
                        load_book = book(path, use_gzip)
                        #if hasattr(load_book, 'bookmarks'):
                        self.books.append(load_book)
        for directory in dirs:
            _fetch(directory)

    @actions.action(type=actions.TYPE_TOGGLE,
                    stock_id='gtk-library',
                    label='Documentation Library')
    def act_documentation_library(self, action):
        """View the documentation library."""
        if action.get_active():
            self.__view = self.create_view('Library')
            for book in self.books:
                self.__view.book_found(book)
            self.__view.books_done()
            self.show_view(view=self.__view)
        else:
            if self.__view is not None:
                self.view_close(self.__view)

    def get_action(self):
        return self.action_group.get_action('library+documentation_library')

    def view_closed(self, view):
        self.__view = None
        self.get_action().set_active(False)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_view" action="base_view_menu" >
                    <placeholder name="ViewMenu">
                        <menuitem action="library+documentation_library" />
                    </placeholder>
                </menu>

                </menubar>
               """


class title_handler(xml.sax.handler.ContentHandler):

    def __init__(self):
        self.title = 'untitled'
        self.is_finished = False

    def startElement(self, name, attributes):
        self.title = attributes['title']
        self.is_finished = True


class book(object):

    def __init__(self, path, include_gz=True):
        self.directory = path
        self.key = path
        self.name = os.path.basename(path)
        self.bookmarks = None
        try:
            self.short_load()
        except (OSError, IOError):
            pass

    def short_load(self):
        config_path = None
        path = self.directory
        if not os.path.isdir(path):
            return
        for name in os.listdir(path):
            if name.endswith('.devhelp'):
                config_path = os.path.join(path, name)
                break
            elif name.endswith('.devhelp.gz'):
                gz_path = os.path.join(path, name)
                f = gzip.open(gz_path, 'rb', 1)
                gz_data = f.read()
                f.close()
                fd, config_path = tempfile.mkstemp()
                os.write(fd, gz_data)
                os.close(fd)
                break
        self.title = None
        if config_path:
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_external_ges, 0)
            handler = title_handler()
            parser.setContentHandler(handler)
            f = open(config_path)
            for line in f:
                try:
                    parser.feed(line)
                except:
                    raise
                if handler.is_finished:
                    break
            f.close()
            self.title = handler.title
        if not self.title:
            self.title = os.path.basename(path)

    def load(self):
        config_path = None
        path = self.directory
        for name in os.listdir(path):
            if name.endswith('.devhelp'):
                config_path = os.path.join(path, name)
                break
            elif name.endswith('.devhelp.gz'):
                gz_path = os.path.join(path, name)
                f = gzip.open(gz_path, 'rb', 1)
                gz_data = f.read()
                f.close()
                fd, config_path = tempfile.mkstemp()
                os.write(fd, gz_data)
                os.close(fd)
                break
        if config_path and os.path.exists(config_path):
            dom = minidom.parse(config_path)
            main = dom.documentElement
            book_attrs = dict(main.attributes)
            for attr in book_attrs:
                setattr(self, attr, book_attrs[attr].value)
            self.chapters = dom.getElementsByTagName('chapters')[0]
            self.root = os.path.join(self.directory, self.link)
            self.bookmarks = self.get_bookmarks()
        else:
            for index in ['index.html']:
                indexpath = os.path.join(path, index)
                if os.path.exists(indexpath):
                    self.root = indexpath
                    break
                self.root = indexpath
        self.key = path

    def get_bookmarks(self):
        #sub = self.chapters.getElementsByTagName('sub')[0]
        root = book_mark(self.chapters, self.directory)
        root.name = self.title
        root.path = self.root
        return root


class book_mark(object):

    def __init__(self, node, root_path):
        try:
            self.name = node.attributes['name'].value
        except:
            self.name = None
        try:
            self.path = os.path.join(root_path, node.attributes['link'].value)
        except:
            self.path = None
        self.key = self.path
        self.subs = []
        for child in self._get_child_subs(node):
            bm = book_mark(child, root_path)
            self.subs.append(bm)

    def _get_child_subs(self, node):
        return [n for n in node.childNodes if n.nodeType == 1]


Service = document_library
