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
import pida.pidagtk.contentbook as contentbook

class Editor(editor.Editor):
    NAME = 'culebra' 

    def init(self):
        self.__views = {}
        self.__currentview = None
        self.__bufferevents = []

    def launch(self):
        self.manager.emit_event('started')

    def open_file(self, filename):
        if not filename in self.__views:
            view = edit.EditWindow(self)
            view.load_file(filename)
            view.get_main_window = lambda: self.boss.get_main_window()
            view.show_all()
            contentview = contentbook.EditorView(view, filename)
            contentview.connect('action', self.cb_view_action)
            self.boss.command('editor', 'add-page', contentview=contentview)
            self.__views[filename] = contentview
        else:
            self.__views[filename].raise_tab()
        self.__currentview = self.__views[filename]

    def open_file_line(self, filename, linenumber):
        #self.__bufferevents.append([self.goto_line, (linenumber, )])
        self.open_file(filename)
        self.goto_line(linenumber)

    def goto_line(self, linenumber):
        print 'goto', linenumber
        buf = self.__currentview.editor.get_current()
        print buf.filename
        titer = buf.get_iter_at_line(linenumber - 1)
        self.__currentview.editor.editor.scroll_to_iter(titer, 0.1)
        buf.place_cursor(titer)
        self.__currentview.editor.grab_focus()

    def save_view(self, view):
        view.editor.file_save()
        self.boss.command('buffer-manager', 'reset-current-buffer')

    def save_current(self):
        self.__save_view(self.__currentview)

    def save_file(self, filename):
        if filename in self.__views:
            self.__save_view(self.__views[filename])
        else:
            self.log_warn("File is not loaded.")

    def __get_view(self):
        return self.__view
    view = property(__get_view)

    def cb_view_action(self, contentview, action):
        if action == 'open':
            self.boss.command('filemanager', 'browse', directory='')
        elif action == 'save':
            self.save_view(contentview)

    def culebra_file_opened(self, filename):
        print filename, self.__bufferevents
        for fcall, args in self.__bufferevents:
            fcall(*args)
        self.__bufferevents = []
        self.manager.emit_event('file-opened', filename=filename)
       
