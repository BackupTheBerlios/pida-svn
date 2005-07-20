# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id$
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
import pida.configuration.config as config
import pida.configuration.registry as registry

import edit

class Plugin(plugin.Plugin):
    NAME = 'Culebra'    
    DICON = 'configure', 'Configure Pida'

    def do_init(self):
        self.editor = None
        self.bufferlist = None
        self.currentbufnum = None

    def configure(self, reg):
        self.local_registry = reg.add_group('culebra',
            'Options pertaining to the Culebra text editor')
        self.local_registry.add('font',
                registry.Font,
                'Monospace 10',
                'The Font used by Culebra')
        
        

    def launch(self):
        self.create_editor()
        self.edit_getbufferlist()

    def create_editor(self):
        if not self.editor:
            self.editor = edit.EditWindow(self.cb, self)
            self.cb.embedwindow.add(self.editor)
            self.editor.show_all()
        
    def populate_widgets(self):
        pass

    def cb_alternative(self, *args):
        self.do_action('showconfig')
    
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
        try:
            buff, text, model = self.editor.wins[fname]
            manager = buff.get_data('languages-manager')
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
        except:
            pass
        return 'None'

    def evt_started(self):
        self.launch()
        
    def evt_debuggerframe(self, frame):
        if not frame.filename.startswith('<'):
            if frame.filename != self.editor.get_current()[0]:
                self.do_edit('openfile', frame.filename)
            self.do_edit('gotoline', frame.lineno - 1)
        
    def edit_getbufferlist(self):
        bl = []
        L = self.editor.wins.keys()
        L.sort()
        for i in L:
            buff, fname = self.editor.wins[i]
            bl.append([i, fname])
        self.bufferlist = bl
        self.cb.evt('bufferlist', bl)

    def abspath(self, filename):
        if filename and not filename.startswith('/'):
            filename = os.path.join(os.getcwd(), filename)
        return filename

    def edit_getcurrentbuffer(self):
        cb = self.abspath(self.editor.get_current()[1])
        for i, filename in self.bufferlist:
            if filename == cb:
                self.cb.evt('bufferchange', i, filename)
                break

    def edit_changebuffer(self, num):
        print self.editor.current_buffer, num
        if self.editor.current_buffer != num:
            self.editor.current_buffer = num
            buff, fname = self.editor.get_current()
            self.editor.editor.set_buffer(buff)
            self.do_evt('bufferchange', num, fname)

    def edit_closebuffer(self):
        self.editor.file_close()

    def edit_gotoline(self, line):
        buf = self.editor.get_current()[0]
        titer = buf.get_iter_at_line(line)
        self.editor.editor.scroll_to_iter(titer, 0.25)
        buf.place_cursor(titer)
        self.editor.editor.grab_focus()

    def edit_openfile(self, filename):
        self.editor.load_file(filename)
        self.editor.editor.grab_focus()
