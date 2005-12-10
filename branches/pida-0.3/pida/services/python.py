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

import os

from pida.core import service

import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree
import pida.utils.pythonparser as pythonparser

defs = service.definitions
types = service.types


class python_source_view(contentview.content_view):

    def init(self):
        self.__nodes = tree.Tree()
        self.__nodes.set_property('markup-format-string',
            "%(name)s")
        self.widget.pack_start(self.__nodes)

    def set_source_nodes(self, root_node):
        self.__nodes.clear()
        self.__set_nodes(root_node)
        
    def __set_nodes(self, root_node, piter=None):
        if root_node.linenumber is not None:
            piter = self.__nodes.add_item(root_node, parent=parent,
                key=(root_node.filename, root_node.linenumber))
        for node in root_node.children:
            self.__set_nodes(node, piter)

class python(service.service):

    lang_view_type = python_source_view

    class python_language(defs.language_handler):

        file_name_globs = ['*.py']

        first_line_globs = ['*/bin/python']

        def act_execute_current_file(self, action):
            pass

        def load_document(self, document):
            root_node = pythonparser.get_nodes_from_string(document.string)
            self.service.lang_view.set_source_nodes(root_node)

    class python(defs.project_type):
    
        class general(defs.optiongroup):
            """General options for Python projects"""
            class source_directory(defs.optiongroup):
                """The directory containing source code."""
                rtype = types.directory
                default = os.path.expanduser('~')
                
Service = python
