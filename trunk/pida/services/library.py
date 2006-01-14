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

import gtk
import gobject

import pida.core.service as service

import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree

import xml.dom.minidom as minidom

import tempfile
import gzip

import threading

import pida.utils.gforklet as gforklet

defs = service.definitions
types = service.types

class lib_list(tree.Tree):

    pass
    #SORT_LIST = ['name', 'title']

class bookmark_view(contentview.content_view):

    ICON_NAME = 'library'
    LONG_TITLE = 'Documentation Library'

    HAS_CONTROL_BOX = False

    def init(self):
        self.__list = lib_list()
        self.__list.set_property('markup_format_string',
                                 '%(name)s')
        self.__list.connect('double-clicked', self.cb_booklist_clicked)
        self.widget.pack_start(self.__list)
        self.long_title = 'Loading books...'

    def book_found(self, bookroot):
        if bookroot is not None:
            def _add():
                self._add_item(bookroot)
            gobject.idle_add(_add)
        else:
            self.books_done()

    def books_done(self):
        self.__list.show_all()
        self.long_title = 'Documentation library'

    def _add_item(self, item, parent=None):
        niter = self.__list.add_item(item, parent=parent)
        for child in item.subs:
            self._add_item(child, niter)
        
    def cb_booklist_clicked(self, treeview, item):
        book = item.value
        if book.path:
            self.service.boss.call_command('webbrowse', 'browse',
                                       url=book.path)
        else:
            self.service.log.info('Bad document book "%s"', book.name)

class document_library(service.service):

    display_name = 'Documentation Library'

    plugin_view_type = bookmark_view

    class book_locations(defs.optiongroup):
        """Locations of books in the file system."""
        class use_gzipped_book_files(defs.option):
            """Whether to use devhelp.gz format books."""
            rtype = types.boolean
            default = True

    def init(self):
        gobject.timeout_add(10000, self.fetch)

    def fetch_thread(self):
        def t():
            for bookmarks in self.fetch_books()():
                self.plugin_view.book_found(bookmarks)
        t = threading.Thread(target=t)
        t.start()

    def fetch_forklet(self):
        gforklet.fork_generator(self.fetch_books(), [],
                                self.plugin_view.book_found)

    def fetch(self):
        self.fetch_thread()

    def fetch_books(self):
        pida_directory = os.path.join(self.boss.pida_home, 'library')
        dirs = [pida_directory, '/usr/share/gtk-doc/html',
                                '/usr/share/devhelp/books',
                                os.path.expanduser('~/.devhelp/books')]
        use_gzip = self.opt('book_locations', 'use_gzipped_book_files')
        def gen():
            for directory in dirs:
                if os.path.exists(directory):
                    for name in os.listdir(directory):
                        path = os.path.join(directory, name)
                        if os.path.exists(path):
                            load_book = book(path, use_gzip)
                            if hasattr(load_book, 'bookmarks'):
                                yield load_book.bookmarks
            yield None
        return gen

class book(object):

    def __init__(self, path, include_gz=True):
        self.directory = path
        self.root = None
        config_path = None
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
        self.name = os.path.basename(path)
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
