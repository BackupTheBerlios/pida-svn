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

import pida.core.editor as editor
import culebra.edit as edit

class Editor(editor.Editor):
    NAME = 'culebra' 

    def populate(self):
        self.__view = edit.EditWindow(self)
        self.__view.show_all()

    def launch(self):
        self.manager.emit_event('started')

    def open_file(self, filename):
        self.__view.load_file(filename)
        entries = self.__view.entries
        if entries.get_selected().filename != filename:
            for index, entry in enumerate(entries):
                if entry.filename == filename:
                    entries.selected_index = index
                    buff = entries.selected
                    self.__view.editor.scroll_to_mark(buff.get_insert(), 0.25)
                    self.__view.editor.grab_focus()

    def __get_view(self):
        return self.__view
    view = property(__get_view)
