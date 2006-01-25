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

import pida.core.service as service
import compiler
import sys

defs = service.definitions

import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree

import pida.utils.pyflakes as pyflakes

import textwrap
import threading

class pyflake_view(contentview.content_view):

    ICON_NAME = 'gtk-info'

    HAS_CONTROL_BOX = False

    LONG_TITLE = 'Python errors'

    def init(self):
        self.__list = tree.Tree()
        self.__list.set_property('markup-format-string',
            '%(lineno)s %(message_string)s')
        self.widget.pack_start(self.__list)
        self.__list.connect('double-clicked', self.cb_source_clicked)
    
    def set_messages(self, messages):
        self.__list.clear()
        if messages is None:
            return
        for message in messages:
            args = [('<b>%s</b>' % arg) for arg in message.message_args]
            msg = textwrap.wrap(message.message % tuple(args), 25)
            message.message_string = '\n'.join(msg)
            self.__list.add_item(message, key=message)

    def cb_source_clicked(self, treeview, item):
        self.service.boss.call_command('editormanager', 'goto_line',
                                        linenumber=item.value.lineno)

class pyflaker(service.service):

    lang_view_type = pyflake_view

    class pyflakes(defs.language_handler):

        file_name_globs = ['*.py']

        first_line_globs = ['*python*']

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
                              code_string=document.string,
                              filename=document.filename)
                self.service.lang_view.set_messages(messages)
                self.__cached[document.unique_id] = (messages,
                               document.stat.st_mtime)
            if messages is None:
                t = threading.Thread(target=load)
                t.run()
            else:
                self.service.lang_view.set_messages(messages)

    def cmd_check(self, code_string, filename):
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
            #w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
            return w.messages


def checkPath(filename):
    return check(file(filename).read(), filename)


Service = pyflaker

