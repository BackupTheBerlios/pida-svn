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

# pidagtk import(s)
import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview


defs = service.definitions
types = service.types

class todo_hint(object):

    def __init__(self, line, linenumber, marker):
        self.key = linenumber
        self.line = line
        self.linenumber = linenumber
        self.marker = marker

class todo_view(contentview.content_view):
    
    LONG_TITLE = 'Todo Viewer'
    ICON_NAME = 'list'

    HAS_CONTROL_BOX = False

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
    
class todo(service.service):
    
    lang_view_type = todo_view

    display_name = 'TODO List'

    class todo_definition(defs.optiongroup):
        class use_TODO(defs.option):
            """Whether the TODO search will use 'TODO' statements"""
            rtype = types.boolean
            default = True
        class use_FIXME(defs.option):
            """Whether the TODO search will use 'FIXME' statements"""
            rtype = types.boolean
            default = True
        class additional_markers(defs.option):
            """Additional markers that will be used for TODO searching. (comma separated list)"""
            rtype = types.string
            default = ''

    class todolist(defs.language_handler):

        file_name_globs = ['*']

        first_line_globs = []

        def init(self):
            self.__document = None
            self.cached = self.__cached = {}

        def load_document(self, document):
            self.__document = document
            messages = None
            if document.unique_id in self.__cached:
                messages, mod = self.__cached[document.unique_id]
                if mod != document.stat.st_mtime:
                    messages = None
            def load():
                messages = self.service.call('check',
                              lines=document.lines)
                self.service.lang_view.set_messages(messages)
                self.__cached[document.unique_id] = (messages,
                               document.stat.st_mtime)
            if messages is None:
                t = threading.Thread(target=load)
                t.run()
            else:
                self.service.lang_view.set_messages(messages)

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
