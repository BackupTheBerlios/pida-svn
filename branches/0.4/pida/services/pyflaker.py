# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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

import compiler, sys, textwrap, threading
import gtk, gobject

from pida.pidagtk import tree
from pida.core import service, actions, document
from pida.pidagtk import contentview
from pida.utils import pyflakes
defs = service.definitions

from pida.model import attrtypes as types



class FlakeTree(tree.Tree):

    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Line Number', 'lineno'),
                      ('Error Type', 'name'),
                      ('Message', 'message_string')]



class PyflakeView(contentview.content_view):

    ICON_NAME = 'gtk-info'

    HAS_CONTROL_BOX = True

    LONG_TITLE = 'Python errors'
    SHORT_TITLE = 'Py Errors'
    
    last_check = None

    def init(self):
        self.__list = FlakeTree()
        self.__list.set_property('markup-format-string',
            '<tt>%(lineno)s </tt><i>%(name)s</i>'
            '\n%(message_string)s')
        self.widget.pack_start(self.__list)
        self.__list.connect('double-clicked', self.cb_source_clicked)
    
    def set_messages(self, messages):
        self.__list.clear()
        if messages is None:
            return
        for message in messages:
            message.name = message.__class__.__name__
            args = [('<b>%s</b>' % arg) for arg in message.message_args]
            message.message_string = message.message % tuple(args)
            self.__list.add_item(message, key=message)
    
    def cb_source_clicked(self, treeview, item):
        self.service.boss.call_command('editormanager', 'goto_line',
                                        linenumber=item.value.lineno - 1)

    

class pyflaker(service.service):

    display_name = 'Python Error Checking'

    class PyflakeView(defs.View):
        view_type = PyflakeView
        book_name = 'plugin'

    def init(self):
        self._cache = document.DocumentCache(self._check)
        self.counter = 0
        self.__view = None
        self._currentdocument = None

    def reset(self):
        self.action_group.get_action('pyflaker+show').set_active(True)

    @actions.action(
        type=actions.TYPE_TOGGLE,
        label="Error Viewer",
        stock_id=gtk.STOCK_DIALOG_WARNING,
        )
    def act_show(self, action):
        if action.get_active():
            if self.__view is None:
                self.__view = self.create_view('PyflakeView')
                self.__view.show()
            else:
                self.__view.raise_page()
            if self._currentdocument is not None:
                self.load_document(self._currentdocument)
        else:
            if self.__view is not None:
                self.__view.close()
            self.__view = None

    def load_document(self, document):
        self._currentdocument = document
        if document.is_new:
            return
        if self.__view is None:
            return
        self.counter += 1
        def new_thread(counter):
            result = self._cache.get_result(document)
            gobject.idle_add(self._update_node, (counter, result))
        threading.Thread(target=new_thread, args=(self.counter,)).start()

    def _check(self, document):
        code_string = document.string
        filename = document.filename
        try:
            tree = compiler.parse(code_string)
        except (SyntaxError, IndentationError):
            value = sys.exc_info()[1]
            (lineno, offset, line) = value[1][1:]
            if line.endswith("\n"):
                line = line[:-1]
            print >> sys.stderr, line
            print >> sys.stderr, " " * (offset-2), "^"
        else:
            w = pyflakes.Checker(tree, filename)
            return w.messages

    def view_closed(self, view):
        self.__view = None
        self.action_group.get_action('pyflaker+show').set_active(False)

    def bnd_buffermanager_document_modified(self, document):
        if self._currentdocument is document:
            self.load_document(document)

    def bnd_buffermanager_document_changed(self, document):
        self.load_document(document)

    def _update_node(self, args):
        counter, root_node = args
        if self.counter != counter:
            return
        self.__view.set_messages(root_node)

    def get_menu_definition(self):
        return """
                <menubar>
                    <menu action="base_python_menu" name="base_python">
                        <menuitem action="pyflaker+show" />
                    </menu>
                </menubar>
               """

Service = pyflaker

