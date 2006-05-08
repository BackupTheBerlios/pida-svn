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

import thread

import gobject
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

    HAS_CONTROL_BOX = True
    LONG_TITLE = 'Python source browser'
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
        # TODO: if the root_node has *alot* of elements this will be
        # TODO: slow, we need to split it in chunks
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

    class PythonBrowser(defs.View):
        view_type = python_source_view
        book_name = 'plugin'

    def init(self):
        self.__view = None
        self.counter = 0

    def get_plugin_view(self):
        return self.__view
    plugin_view = property(get_plugin_view)

    def reset(self):
        self._visact = self.action_group.get_action(
            'pythonbrowser+python_browser')
        self._visact.set_active(True)

    def _update_node(self, args):
        counter, root_node = args
        # Here we test if the thread id is the one we're expecting
        # if it's not just discard it silentely
        if self.counter != counter:
            return
            
        self.__view.set_source_nodes(root_node)
    
    def load_document(self, document):
        if self.__view is None:
            return
            
        self.__document = document
        if document.is_new:
            return
        
        # This counter is used so that no out-of sync trees get feed into
        # the main loop. This way if the finished thread is the one we're
        # waiting for.
        self.counter += 1
        
        def new_thread(counter):
            root_node = pythonparser.get_nodes_from_string(document.string)
            # important: ui code must be done inside main loop
            if root_node is not None:
                gobject.idle_add(self._update_node, (counter, root_node))
            
        thread.start_new_thread(new_thread, (self.counter,))

    @actions.action(type=actions.TYPE_TOGGLE,
                    stock_id='gtk-library',
                    label='Python Browser')
    def act_python_browser(self, action):
        """View the documentation library."""
        self.set_view_visible(action.get_active())

    def set_view_visible(self, visibility):
        if visibility:
            if self.__view is None:
                self.__view = self.create_view('PythonBrowser')
                self.show_view(view=self.__view)
            self.__view.raise_page()
        else:
            if self.__view is not None:
                self.close_view(self.__view)
            self.__view = None

    def bnd_buffermanager_document_changed(self, document):
        self.load_document(document)

    def bnd_buffermanager_document_modified(self, document):
        self.load_document(document)

    def view_closed(self, view):
        self.__view = None
        self._visact.set_active(False)

    def get_menu_definition(self):
        return """
            <menubar>
            <menu name="base_python" action="base_python_menu">
            <menuitem name="viewpybrowse" action="pythonbrowser+python_browser" />
            </menu>
            </menubar>
            """

Service = PythonBrowser


