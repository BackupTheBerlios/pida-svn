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

import pida.core.service as service

import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree

defs = service.definitions
types = service.types

class bookmark_view(contentview.content_view):

    def init(self):
        self.__list = tree.Tree()
        self.__list.set_property('markup_format_string',
                                 '%(name)s')
        self.__list.connect('double-clicked', self.cb_booklist_clicked)
        self.widget.pack_start(self.__list)
        for book in self.service.get_books():
            self.__list.add_item(book)
        
    def cb_booklist_clicked(self, treeview, item):
        book = item.value
        if book.root:
            self.service.boss.call_command('webbrowse', 'browse',
                                       url=book.root)
        else:
            self.service.log.info('Bad document book "%s"', book.name)

class document_library(service.service):

    plugin_view_type = bookmark_view

    def init(self):
        pass

    def get_books(self):
        books = []
        directory = os.path.join(self.boss.pida_home, 'library')
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            books.append(book(path))
        return books

class book(object):

    def __init__(self, path):
        self.directory = path
        self.root = None
        for index in ['index.html']:
            indexpath = os.path.join(path, index)
            if os.path.exists(indexpath):
                self.root = indexpath
                break
        self.name = os.path.basename(path)
        self.key = path

Service = document_library
