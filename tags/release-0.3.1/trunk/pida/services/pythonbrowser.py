# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

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

import threading

import pida.core.actions as actions

# pida core import(s)
from pida.core import service

# pida gtk import(s)
import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree

# pida utils import(s)
import pida.utils.pythonparser as pythonparser

if not pythonparser.is_bike_installed():
    raise Exception('Bike is not installed')

defs = service.definitions
types = service.types

class SourceTree(tree.Tree):

    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Line Number', 'linenumber'),
                      ('Name', 'name'),
                      ('Type', 'node_type_short')]

class python_source_view(contentview.content_view):

    ICON_NAME = 'gtk-sourcetree'

    HAS_CONTROL_BOX = False
    LONG_TITLE = 'python source browser'
    SHORT_TITLE = 'Source'

    def init(self):
        self.__nodes = SourceTree()
        self.__nodes.set_property('markup-format-string',
            '<tt><b><i><span color="%(node_colour)s">'
            '%(node_type_short)s </span></i></b>'
            '<b>%(name)s</b>\n%(additional_info)s</tt>')
        self.widget.pack_start(self.__nodes)
        self.__nodes.connect('double-clicked', self.cb_source_clicked)

    def set_source_nodes(self, root_node):
        exp_paths = []
        e_paths = []
        def f(row, path):
            e_paths.append(path)
        self.__nodes.view.map_expanded_rows(f)
        self.__nodes.clear()
        self.__set_nodes(root_node)
        for path in e_paths:
            self.__nodes.view.expand_row(path, False)
        
    def __set_nodes(self, root_node, piter=None):
        if root_node.linenumber is not None:
            piter = self.__nodes.add_item(root_node, parent=piter,
                key=(root_node.filename, root_node.linenumber))
        for node in root_node.children:
            self.__set_nodes(node, piter)

    def cb_source_clicked(self, treeview, item):
        self.service.boss.call_command('editormanager', 'goto_line',
                                        linenumber=item.value.linenumber)

class PythonBrowser(service.service):

    lang_view_type = python_source_view

    class python_browser(defs.language_handler):
        file_name_globs = ['*.py']

        first_line_globs = ['*/bin/python']

        def init(self):
            self.__document = None
            self.__cached = self.cached = {}

        def load_document(self, document):
            self.__document = document
            root_node = None
            if document.unique_id in self.__cached:
                root_node, mod = self.__cached[document.unique_id]
                if mod != document.stat.st_mtime:
                    root_node = None
            def load():
                root_node = pythonparser.\
                    get_nodes_from_string(document.string)
                self.service.lang_view.set_source_nodes(root_node)
                self.__cached[document.unique_id] = (root_node,
                               document.stat.st_mtime)
            if not root_node:
                load()
                #t = threading.Thread(target=load)
                #t.run()
            else:
                self.service.lang_view.set_source_nodes(root_node)

    def bnd_buffermanager_document_modified(self, document):
        self.uncache(document)


Service = PythonBrowser


