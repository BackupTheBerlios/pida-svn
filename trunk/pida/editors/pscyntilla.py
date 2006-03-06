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

import gtk

from rat import hig
from gtk import gdk

from pida.pidagtk import contentview
from pida.core import actions
from pida.core import service

import scintilla
import mimetypes

defs = service.definitions
types = service.types

class Pscyntilla(scintilla.Scintilla):

    def set_font(self, fontname, size):
        self.set_base_sc_style(font='Monospace', size=12)
    
    def set_sc_style(self, number, fore=None, back=None, bold=None, font=None,
                    size=None):
        if fore is not None:
            self.style_set_fore(number, self.colour_from_string(fore))
        if back is not None:
            self.style_set_back(number, self.colour_from_string(back))
        if bold is not None:
            self.style_set_bold(number, bold)
        if font is not None:
            self.style_set_font(number, '!%s' % font)
        if size is not None:
            self.style_set_size(number, size)
    
    def set_base_sc_style(self, **kw):
        self.set_sc_style(scintilla.STYLE_DEFAULT, **kw)
        
    def load_file(self, filename):
        f = open(filename, 'r')
        mimetype, n = mimetypes.guess_type(filename)
        if mimetype:
            ftype = mimetype.split('/')[-1].split('-')[-1]
            self.set_lexer_language(ftype)
        self.load_fd(f)

    def load_fd(self, fd):
        for line in fd:
            self.append_text(len(line), line)

   

class ScintillaView(contentview.content_view):

    def init(self):
        sw = gtk.ScrolledWindow()
        self.widget.pack_start(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.editor = Pscyntilla()
        sw.add(self.editor)
        self.optionize()
        
    def optionize(self):
        self.editor.set_font('Monospace', 10)
      

class ScintillaEditor(service.service):    

    display_name = 'Pscyntilla Text Editor'

    class EditorView(defs.View):
        book_name = 'edit'
        view_type = ScintillaView
        
    def init(self):
        self._documents = {}
        self._views = {}
        self._current = None
    
    def cmd_start(self):
        self.get_service('editormanager').events.emit('started')

    def cmd_edit(self, document=None):
        if document.unique_id not in self._views:
            self._load_document(document)
        self._view_document(document)
        
    def _load_document(self, document):
        view = self.create_view('EditorView')
        if not document.is_new:
            view.editor.load_file(document.filename)
        self._views[document.unique_id] = view
        self._documents[view.unique_id] = document
        self.show_view(view=view)
        
    def _view_document(self, document):
        self._current = document
        self._views[document.unique_id].raise_page()
    
Service = ScintillaEditor
