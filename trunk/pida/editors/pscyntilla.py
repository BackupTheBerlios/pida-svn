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
import gtk

from pida.pidagtk import contentview
from pida.core import actions
from pida.core import service

import scintilla
import mimetypes
from pida.utils.culebra.buffers import SafeFileWrite
from keyword import kwlist

defs = service.definitions
types = service.types

class Pscyntilla(scintilla.Scintilla):

    def __init__(self):
        super(Pscyntilla, self).__init__()
        self.set_size_request(0, 0)
        self._set_blue_theme()
        self.show_edge_column()
        self.show_line_numbers()
        self.show_marker_margin()
        self.show_caret()
        self.set_use_tabs(False)
        self.set_indent(4)
        self.connect('margin-click', self.cb_margin_click)
        self._bind_extra_keys()
        
    def _bind_extra_keys(self):
        
        def _kp(widg, *args):
            if args == (122, 4):
                i = self.line_from_position(self.get_current_pos())
                self.toggle_fold(i)
        self.connect('key', _kp)
        
    def _set_blue_theme(self):
        self.set_base_sc_style(fore='606060', back='300000')
        for i in range(32):
            self.set_sc_style(i, back='300000')
        self.set_sc_style(0, fore='a0a0a0')
        self.set_sc_style(1, fore='a0a0a0')
        self.set_sc_style(2, fore='f00000')
        self.set_sc_style(3, fore='c000c0')
        self.set_sc_style(4, fore='c000c0')
        self.set_sc_style(5, fore='f000')
        self.set_sc_style(6, fore='c0c0')
        self.set_sc_style(7, fore='c0c0')
        self.set_sc_style(8, fore='f0f0', bold=True)
        self.set_sc_style(9, fore='f00000', bold=True)
        self.set_sc_style(10, fore='c0')
        self.set_sc_style(11, fore='ffc0c0')
        self.set_sc_style(12, fore='a0a0a0')
        self.set_sel_back(True, self.colour_from_string('400040'))
    
    def set_font(self, fontname, size):
        self.set_base_sc_style(font=fontname, size=size)
    
    def colour_from_string(self, colourstring):
        return int(colourstring, 16)
    
    def show_edge_column(self, size=80):
        self.set_edge_mode(scintilla.EDGE_LINE)
        self.set_edge_colour(self.colour_from_string('f0c0c0'))
        self.set_edge_column(size) 
    
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
        self.filename = filename
        f = open(filename, 'r')
        mimetype, n = mimetypes.guess_type(filename)
        if mimetype:
            ftype = mimetype.split('/')[-1].split('-')[-1]
            self.set_lexer_language(ftype)
            if ftype == 'python':
                self.set_key_words(0, ' '.join(kwlist))
        self.load_fd(f)
        self.empty_undo_buffer()
        self.set_save_point()

    def save(self):
        """Saves the current buffer to the file"""
        assert self.filename is not None
        fd = SafeFileWrite(self.filename)
        txt = self.get_text(self.get_length())[-1]
        fd.write(''.join(txt))
        fd.close()
        self.set_save_point()

    def load_fd(self, fd):
        for line in fd:
            self.append_text(len(line), line)
        self.colourise(0, -1)
   
    def show_line_numbers(self):
        self.set_margin_type_n(0, scintilla.SC_MARGIN_NUMBER)
        self.set_margin_width_n(0, 32)
        self.set_line_number_style(back='400000', fore='a09090')
        
    def show_marker_margin(self):
        #margin 2 for markers
        self.set_property('fold', '1')
        self.set_property("tab.timmy.whinge.level", "1")
        self.set_property("fold.comment.python", "0")
        self.set_property("fold.quotes.python", "0")
        self.set_fold_flags(16)
        self.set_margin_type_n(2, scintilla.SC_MARGIN_SYMBOL)
        self.set_margin_mask_n(2, scintilla.SC_MASK_FOLDERS)
        self.set_margin_sensitive_n(2, True)
        self.set_margin_width_n(2, 14)
        self.set_fold_margin_colour(True, self.colour_from_string('300000'))
        self.set_fold_margin_hi_colour(True, self.colour_from_string('300000'))
        self.marker_define(scintilla.SC_MARKNUM_FOLDEREND,
                           scintilla.SC_MARK_BOXPLUSCONNECTED)
        self.marker_define(scintilla.SC_MARKNUM_FOLDEROPENMID,
                           scintilla.SC_MARK_BOXMINUSCONNECTED)
        self.marker_define(scintilla.SC_MARKNUM_FOLDERMIDTAIL,
                           scintilla.SC_MARK_TCORNER)
        self.marker_define(scintilla.SC_MARKNUM_FOLDERTAIL,
                           scintilla.SC_MARK_LCORNER)
        self.marker_define(scintilla.SC_MARKNUM_FOLDERSUB,
                           scintilla.SC_MARK_VLINE)
        self.marker_define(scintilla.SC_MARKNUM_FOLDER,
                           scintilla.SC_MARK_BOXPLUS)
        self.marker_define(scintilla.SC_MARKNUM_FOLDEROPEN,
                           scintilla.SC_MARK_BOXMINUS)
        for i in range(25, 32):
            self.marker_set_back(i, self.colour_from_string('606060'))
    
    def get_all_fold_headers(self):
        for i in xrange(self.get_line_count()):
            level = self.get_fold_level(i)
            if level & scintilla.SC_FOLDLEVELHEADERFLAG:
                yield i, level
    
    def get_toplevel_fold_headers(self):
        for i, level in self.get_all_fold_headers():
            if level & scintilla.SC_FOLDLEVELNUMBERMASK == 1024:
                yield i
    
    def collapse_all(self):
        for i in self.get_toplevel_fold_headers():
            if self.get_fold_expanded(i):
                self.toggle_fold(i)
    
    def expand_all(self):
        for i in self.get_toplevel_fold_headers():
            if not self.get_fold_expanded(i):
                self.toggle_fold(i)
           
    def set_line_number_style(self, **kw):
        self.set_sc_style(scintilla.STYLE_LINENUMBER, **kw)
        
    def show_caret(self):
        self.set_caret_fore(self.colour_from_string('f0'))
        self.set_caret_line_back(self.colour_from_string('600000'))
        self.set_caret_line_visible(True)
        
    def cb_margin_click(self, ed, mod, pos, margin):
        if margin == 2:
            if mod == 1:
                self.collapse_all()
            elif mod == 6:
                self.expand_all()
            else:
                lineClicked = self.line_from_position(pos)
                if (self.get_fold_level(lineClicked) &
                    scintilla.SC_FOLDLEVELHEADERFLAG):
                    self.toggle_fold(lineClicked)

class ScintillaView(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_TITLE = False

    def init(self):
        sw = gtk.ScrolledWindow()
        self.widget.pack_start(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.editor = Pscyntilla()
        sw.add(self.editor)
        self.optionize()
        self.editor.connect('modified', self.cb_modified)
        self.editor.connect('save-point-reached', self.cb_save_point_reached)
        self.editor.connect('save-point-left', self.cb_save_point_left)

    def cb_save_point_reached(self, editor, *args):
        self.service._save_act.set_sensitive(False)
        self.service._revert_act.set_sensitive(False)

    
    def cb_save_point_left(self, editor, *args):
        self.service._save_act.set_sensitive(True)
        self.service._revert_act.set_sensitive(True)

        print 'savepointleave'    
        
    def optionize(self):
        self.editor.set_font('Monospace', 12)
        
    def cb_modified(self, editor, *args):
        if self.service._current:
            self.service._sensitise_actions()
      

class ScintillaEditor(service.service):    

    display_name = 'Pscyntilla Text Editor'

    class EditorView(defs.View):
        book_name = 'edit'
        view_type = ScintillaView
        
    def init(self):
        self._documents = {}
        self._views = {}
        self._current = None
    
    def reset(self):
        self._bind_document_actions()
    
    def cmd_start(self):
        self.get_service('editormanager').events.emit('started')

    def cmd_edit(self, document=None):
        if document.unique_id not in self._views:
            self._load_document(document)
        self._view_document(document)

    def cmd_save(self):
        self._current.editor.save()
   
    def cmd_save_as(self, filename):
        self._current.editor.filename = filename
        self._current.editor.save()
        
    def cmd_goto_line(self, linenumber):
        e = self._current.editor
        e.goto_line(linenumber - 1)
        wanted = linenumber - (e.lines_on_screen() / 2)
        actual = e.get_first_visible_line()
        e.line_scroll(0, wanted - actual)        
        e.grab_focus()
        
    def cmd_undo(self):
        self._current.editor.undo()

    def cmd_redo(self):
        self._current.editor.redo()

    def cmd_cut(self):
        self._current.editor.cut()

    def cmd_copy(self):
        self._current.editor.copy()

    def cmd_paste(self):
        self._current.editor.paste()
        
    def cmd_close(self, document):
        view = self._views[document.unique_id]
        self.close_view(view)
        self._current = None
        
    def view_closed(self, view):
        if view.unique_id in self._documents:
            doc = self._documents[view.unique_id]
            del self._documents[view.unique_id]
            del self._views[doc.unique_id]
            self.boss.call_command('buffermanager', 'document_closed',
                                   document=doc)

        
    def _load_document(self, document):
        view = self.create_view('EditorView')
        if not document.is_new:
            view.editor.load_file(document.filename)
        self._views[document.unique_id] = view
        self._documents[view.unique_id] = document
        self.show_view(view=view)
        
    def _view_document(self, document):
        view = self._views[document.unique_id]
        self._current = view
        view.raise_page()
        view.editor.grab_focus()
        self._sensitise_actions()
        
    def _bind_document_actions(self):
        actions = self.boss.call_command("documenttypes",
            "get_document_actions")
        for action in actions:
            actname = action.get_name()
            if actname == 'documenttypes+document+undo':
                self._undo_act = action
            elif actname == 'documenttypes+document+redo':
                self._redo_act = action
            elif actname == 'documenttypes+document+revert':
                self._revert_act = action
            elif actname == 'DocumentSave':
                self._save_act = action
            elif actname == 'documenttypes+document+paste':
                self._paste_act = action
    
    def _sensitise_actions(self):
        self._undo_act.set_sensitive(self._current.editor.can_undo())
        self._redo_act.set_sensitive(self._current.editor.can_redo())
        self._paste_act.set_sensitive(self._current.editor.can_paste())
        
    
Service = ScintillaEditor
