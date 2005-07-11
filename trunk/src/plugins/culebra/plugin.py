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

# System imports
import os
import time
# GTK imports
import gtk
import gnomevfs
import gobject
# Pida imports
import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.configuration.registry as registry

import edit

class Plugin(plugin.Plugin):
    NAME = 'Culebra'    

    def do_init(self):
        self.editor = None
        self.bufferlist = None
        self.currentbufnum = None

    def launch(self):
        self.create_editor()
        self.edit_getbufferlist()

    def create_editor(self):
        if not self.editor:
            self.editor = edit.EditWindow(self.cb)
            self.cb.embedwindow.add(self.editor)
            self.editor.show_all()
            self.editor.notebook.connect('switch-page', self.cb_switchbuffer)
        
    def populate_widgets(self):
        pass

    def cb_alternative(self, *args):
        self.cb.action_showconfig()
    
    def cb_switchbuffer(self, notebook, page, number):
        nuber = int(number)
        if len(self.editor.wins) != len(self.bufferlist):
            self.edit_getbufferlist()
        for i, name in self.bufferlist:
            if i == number:
                if i != self.currentbufnum:
                    self.currentbufnum = i
                    self.cb.evt('filetype', number, self.check_mime(name))
                    self.cb.evt('bufferchange', number, name)
                break
    
    def check_mime(self, fname):
        buffer, text, model = self.editor.wins[fname]
        manager = buffer.get_data('languages-manager')
        if os.path.isabs(fname):
            path = fname
        else:
            path = os.path.abspath(fname)
        uri = gnomevfs.URI(path)
        mime_type = gnomevfs.get_mime_type(path) # needs ASCII filename, not URI
        if mime_type:
            language = manager.get_language_from_mime_type(mime_type)
            if language:
                return language.get_name().lower()
        return 'None'

    def evt_started(self):
        self.launch()
        
    def edit_getbufferlist(self):
        bl = []
        for i in range(self.editor.notebook.get_n_pages()):
            page = self.editor.notebook.get_nth_page(i)
            label = self.editor.notebook.get_tab_label_text(page)
            path = self.abspath(label)
            if path:
                bl.append([i, path])
        self.bufferlist = bl
        self.cb.evt('bufferlist', bl)

    def abspath(self, filename):
        if filename and not filename.startswith('/'):
            filename = os.path.join(os.getcwd(), filename)
        return filename

    def edit_getcurrentbuffer(self):
        cb = self.abspath(self.editor.get_current()[0])
        for i, filename in self.bufferlist:
            if filename == cb:
                self.cb.evt('bufferchange', i, filename)
                break

    def edit_changebuffer(self, num):
        if self.editor.notebook.get_current_page() != num:
            self.editor.notebook.set_current_page(num)

    def edit_closebuffer(self):
        self.editor.file_close()

    def edit_gotoline(self, line):
        tv = self.editor.get_current()[2]
        buf = self.editor.get_current()[1]
        titer = tv.get_iter_at_location(1, line)
        tv.scroll_to_iter(titer, 0)
        buf.place_cursor(titer)

    def edit_openfile(self, filename):
        self.editor.load_file(filename)
