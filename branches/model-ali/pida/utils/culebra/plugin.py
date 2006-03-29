# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id: plugin.py 597 2005-10-22 13:38:13Z cogumbreiro $
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
import pango
import gnomevfs
import gobject
# Pida imports
from pida import plugin
from pida import gtkextra
from pida.configuration import config
from pida.configuration import registry

import edit

class Plugin(plugin.Plugin):
    NAME = 'Culebra'    
    DICON = 'configure', 'Configure Pida'

    def configure(self, reg):
        self.personal_registry = reg.add_group('Culebra',
            'Options pertaining to the Culebra Editor')

        self.personal_registry.add('font',
            registry.Font,
            'Monospace 10',
            'The Font used by Culebra Editor')
        self.personal_registry.add('use_autocomplete',
            registry.Boolean,
            False,
            "Use Autocompletion"
        )
        
    def do_init(self):
        self.editor = None
        self.currentbufnum = None

    def populate_widgets(self):
        pass

    ############################################################################
    def launch(self):
        self.create_editor()
        self.edit_getbufferlist()

    def create_editor(self):
        if not self.editor:
            self.editor = edit.EditWindow(self)
            self.pida.embedwindow.add(self.editor)
            self.editor.show()
        
    def cb_alternative(self, *args):
        self.do_action('showconfig')
    
    def check_mime(self, fname):
        try:
            buff = self.editor.get_current()
            manager = buff.languages_manager
            if os.path.isabs(buff.filename):
                path = buff.filename
            else:
                path = os.path.abspath(buff.filename)
            uri = gnomevfs.URI(path)
            mime_type = gnomevfs.get_mime_type(path) # needs ASCII filename, not URI
            if mime_type:
                language = manager.get_language_from_mime_type(mime_type)
                if language:
                    return language.get_name().lower()
        except RuntimeError:
            pass
            # The file was not found
        except Exception, e:
            import traceback
            traceback.print_exc()
        return 'None'

    def abspath(self, filename):
        if filename and not filename.startswith('/'):
            filename = os.path.join(os.getcwd(), filename)
        return filename
    
    ############################################################################
    def evt_reset(self):
        font = self.personal_registry.font.value()
        font_desc = pango.FontDescription(font)
        if font_desc:
            self.editor.editor.modify_font(font_desc)
        
        self.editor.use_autocomplete = self.personal_registry.use_autocomplete.value()

    def evt_started(self):
        self.launch()
        
    def evt_debuggerframe(self, frame):
        if not frame.filename.startswith('<'):
            if frame.filename != self.editor.get_current().filename:
                self.do_edit('openfile', frame.filename)
            self.do_edit('gotoline', frame.lineno - 1)

    ############################################################################
    def edit_getbufferlist(self):
        if self.editor is None:
            bl = []
        else:
            bl = [(i, v.filename) for (i, v) in enumerate(self.editor.entries)]
        self.do_evt('bufferlist', bl)

    def edit_getcurrentbuffer(self):
        if self.editor is None:
            return
            
        entries = self.editor.entries
        index = entries.selected_index
        entry = entries.selected
        if not entry is None: 
            self.do_evt('filetype', index, self.check_mime(entry.filename))
            self.do_evt('bufferchange', index, entry.filename)

    def edit_changebuffer(self, index):
        if self.editor is None:
            return
            
        entries = self.editor.entries
        
        if entries.selected_index == index:
            return
        
        self.editor.entries.selected_index = index
        buff = entries.selected
        self.edit_getcurrentbuffer()
        self.editor.editor.scroll_to_mark(buff.get_insert(), 0.25)
        self.editor.editor.grab_focus()

    def edit_closebuffer(self):
        self.editor.file_close()
        buf = self.editor.get_current()
        if buf is None:
            self.editor.file_new()


    def edit_gotoline(self, line):
        buf = self.editor.get_current()
        titer = buf.get_iter_at_line(line)
        self.editor.editor.scroll_to_iter(titer, 0.25)
        buf.place_cursor(titer)
        self.editor.editor.grab_focus()

	def edit_newfile(self):
		buf = self.editor.get_current()
		b.set_text("")
		self.editor.file_new()

    def edit_openfile(self, filename):
        self.editor.load_file(filename)
