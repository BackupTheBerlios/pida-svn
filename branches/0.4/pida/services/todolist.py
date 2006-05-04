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

# system import(s)
import threading

# pida core import(s)
import pida.core.service as service
from pida.core import actions

# pidagtk import(s)
import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview


defs = service.definitions

from pida.model import attrtypes as types

class todo_hint(object):

    def __init__(self, line, linenumber, marker):
        self.key = linenumber
        self.line = line
        self.linenumber = linenumber
        self.marker = marker

class todo_view(contentview.content_view):
    
    LONG_TITLE = 'Todo Viewer'
    SHORT_TITLE = 'TODO'
    ICON_NAME = 'gtk-todo'

    HAS_CONTROL_BOX = True

    def init(self):
        self.__list = tree.Tree()
        self.widget.pack_start(self.__list)
        self.__list.set_property('markup-format-string',
                                 '<tt>%(linenumber)s </tt>'
                                 '(<span color="#0000c0">%(marker)s</span>)\n'
                                 '<b>%(line)s</b>')
        self.__list.connect('double-clicked', self.cb_list_d_clicked)

    def set_messages(self, messages):
        self.__list.clear()
        for message in messages:
            self.__list.add_item(message)

    def cb_list_d_clicked(self, tree, item):
        self.service.boss.call_command('editormanager', 'goto_line',
                                        linenumber=item.value.linenumber)


class TodoConfig:
    __order__ = ['todo_definition']
    class todo_definition(defs.optiongroup):
        """Options for the TODO viewer"""
        label = 'Definition of a "TODO"'
        __order__ = ['use_TODO', 'use_FIXME', 'additional_markers']
        class use_TODO(defs.option):
            """Whether the TODO search will use 'TODO' statements"""
            rtype = types.boolean
            default = True
            label = 'use the string "TODO"'
        class use_FIXME(defs.option):
            """Whether the TODO search will use 'FIXME' statements"""
            rtype = types.boolean
            default = True
            label = 'use the string "FIXME"'
        class additional_markers(defs.option):
            """Additional markers that will be used for TODO searching. (comma separated list)"""
            rtype = types.string
            default = ''
            label = 'Additional markers'

    def __markup__(self):
        return 'Todo Viewer'

class todo(service.service):
    
    config_definition = TodoConfig
    
    class TODO(defs.View):
        view_type = todo_view
        book_name = 'plugin'

    def init(self):
        self._view = None

    display_name = 'TODO List'

    def reset(self):
        self._visact = self.action_group.get_action('todolist+todo_viewer')
        self._visact.set_active(True)

    def load_document(self, document):
        self.__document = document
        messages = self.cmd_check(lines=document.lines)
        self._view.set_messages(messages)

    def cmd_check(self, lines):
        """Check the given lines for TODO messages."""
        messages = []
        for i, line in enumerate(lines):
            for marker in self.__get_markers():
                if marker in line:
                    pre, post = line.split(marker, 1)
                    todo = post.strip().strip(':').strip()
                    messages.append(todo_hint(todo, i + 1, marker))
        return messages

    @actions.action(type=actions.TYPE_TOGGLE,
                    stock_id='gtk-todo',
                    label='TODO Viewer')
    def act_todo_viewer(self, action):
        """View the documentation library."""
        self.set_view_visible(action.get_active())

    def set_view_visible(self, visibility):
        if visibility:
            if self._view is None:
                self._view = self.create_view('TODO')
                self.show_view(view=self._view)
            self._view.raise_page()
        else:
            if self._view is not None:
                self.close_view(self._view)

    def view_closed(self, view):
        self._view = None
        self._visact.set_active(False)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_view" action="base_view_menu" >
                    <placeholder name="TopViewMenu">
                        <menuitem action="todolist+todo_viewer" />
                    </placeholder>
                </menu>

                </menubar>
               """

    def __get_markers(self):
        if self.opt('todo_definition', 'use_TODO'):
            yield 'TODO'
        if self.opt('todo_definition', 'use_FIXME'):
            yield 'FIXME'
        for s in self.opt('todo_definition', 'additional_markers').split(','):
            marker = s.strip()
            if marker:
                yield marker

Service = todo
