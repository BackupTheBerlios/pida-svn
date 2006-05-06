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

"""
keyboard shorcuts

undo: ctrl-z
redo: ctrl-shift-z

cut: ctrl-x
copy: ctrl-c
paste: ctrl-v

select: shift-arrow
rectangular select: shift-alt-arrow

Magnify text size.	Ctrl+Keypad+
Reduce text size.	Ctrl+Keypad-
Restore text size to normal.	Ctrl+Keypad/
Indent block.	Tab
Dedent block.	Shift+Tab
Delete to start of word.	Ctrl+BackSpace
Delete to end of word.	Ctrl+Delete
Delete to start of line.	Ctrl+Shift+BackSpace
Delete to end of line.	Ctrl+Shift+Delete
Go to start of document.	Ctrl+Home
Extend selection to start of document.	Ctrl+Shift+Home
Go to start of display line.	Alt+Home
Extend selection to start of display line.	Alt+Shift+Home
Go to end of document.	Ctrl+End
Extend selection to end of document.	Ctrl+Shift+End
Go to end of display line.	Alt+End
Extend selection to end of display line.	Alt+Shift+End
Scroll up.	Ctrl+Up
Scroll down.	Ctrl+Down
Line cut.	Ctrl+L
Line copy.	Ctrl+Shift+T
Line transpose with previous.	Ctrl+T
Selection duplicate.	Ctrl+D
Previous paragraph. Shift extends selection.	Ctrl+[
Next paragraph. Shift extends selection.	Ctrl+]
Previous word. Shift extends selection.	Ctrl+Left
Next word. Shift extends selection.	Ctrl+Right
Previous word part. Shift extends selection	Ctrl+/
Next word part. Shift extends selection.	Ctrl+\

extra:
togle fold: alt-z
control-s: save
"""

import gtk

from rat import hig
from gtk import gdk
import gtk

from pida.pidagtk import contentview
from pida.core import actions
from pida.core import service
from pida.utils.pscyntilla import Pscyntilla
from pida.model import attrtypes as types
defs = service.definitions
#types = service.types



class ScintillaView(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_TITLE = False

    def init(self):
        self.editor = Pscyntilla()
        self.widget.pack_start(self.editor._sc)
        self.optionize()
        self.editor._sc.connect('modified', self.cb_modified)
        self.editor._sc.connect('save-point-reached', self.cb_save_point_reached)
        self.editor._sc.connect('save-point-left', self.cb_save_point_left)

    def cb_save_point_reached(self, editor, *args):
        self.service._save_act.set_sensitive(False)
        self.service._revert_act.set_sensitive(False)
    
    def cb_save_point_left(self, editor, *args):
        self.service._save_act.set_sensitive(True)
        self.service._revert_act.set_sensitive(True)
        
    def optionize(self):
        opt = self.service.opt
        options = self.service.options
        editor = self.editor
        
        # font
        font_and_size = self._font_and_size(options.font.editor_font)
        editor.set_font(*font_and_size)
        
        # indenting options
        indenting = options.indenting
        editor.set_use_tabs(indenting.use_tabs)
        editor.set_tab_width(indenting.tab_width)
        if not indenting.use_tabs:
            editor.set_spaceindent_width(indenting.space_indent_width)
            
        # folding options
        folding = options.folding
        width = folding.marker_size
        editor.use_folding(folding.use_folding, width=width)
        back = folding.marker_background
        fore = folding.marker_foreground
        editor.set_foldmargin_colours(back=back, fore=fore)
        
        # line numbers
        line_numbers = options.line_numbers

        bg = line_numbers.background
        fg = line_numbers.foreground
        editor.set_linenumber_margin_colours(background=bg, foreground=fg)
            
        editor.set_linenumbers_visible(line_numbers.show_line_numbers)
        
        # color options
        if options.colors.use_dark_theme:
            editor.use_dark_theme()
        else:
            editor.use_light_theme()
            
        # caret and selection
        caret = options.caret
        
        editor.set_caret_colour(caret.caret_colour)
        
        color = caret.current_line_color
        highlight = caret.highlight_current_line
        editor.set_caret_line_visible(highlight, color)
        
        editor.set_selection_color(caret.selection_color)
        
        # edge column
        edge_line = options.edge_line
        editor.set_edge_column_visible(edge_line.show_edge_line,
                                       edge_line.position,
                                       edge_line.color)

    def _font_and_size(self, fontdesc):
        name, size = fontdesc.rsplit(' ', 1)
        size = int(size)
        return name, size
        
    def cb_modified(self, editor, *args):
        if self.service._current:
            self.service._sensitise_actions()


class ScintillaConf:    
    __markup__ = lambda self: "Scintilla Editor"

    class font(defs.optiongroup):
        """The font used in the editor"""
        class editor_font(defs.option):
            """The font used in the editor"""
            rtype = types.font
            default = 'Monospace 12'
            
    class indenting(defs.optiongroup):
        """Indenting options"""
        
        class use_tabs(defs.option):
            """Use tabs for indenting"""
            rtype = types.boolean
            default = False
        class tab_width(defs.option):
            """Width of tabs"""
            rtype = types.intrange(1, 16, 1)
            default = 4
        class space_indent_width(defs.option):
            """With of space indents, if not using tabs."""
            rtype = types.intrange(1, 16, 1)
            default = 4
    
    class line_numbers(defs.optiongroup):
        """Options relating to line numbers and the line number margin."""
        class show_line_numbers(defs.option):
            """Whether line numbers will be shown."""
            rtype = types.boolean
            default = True
        class background(defs.option):
            """The line number margin background colour"""
            rtype = types.color
            default = '#e0e0e0'
        class foreground(defs.option):
            """The line number margin foreground colour"""
            rtype = types.color
            default = '#a0a0a0'

    class colors(defs.optiongroup):
        """Options for colours."""
        
        class use_dark_theme(defs.option):
            """Use a dark scheme"""
            rtype = types.boolean
            default = False

    class folding(defs.optiongroup):
        """Options relating to code folding"""
        
        class use_folding(defs.option):
            """Use folding"""
            rtype = types.boolean
            default = True
        class marker_size(defs.option):
            """Marker size"""
            rtype = types.intrange(8, 32, 1)
            default = 14
        class marker_background(defs.option):
            """Marker Background"""
            rtype = types.color
            default = '#e0e0e0'
        class marker_foreground(defs.option):
            rtype = types.color
            default = '#a0a0a0'

    class caret(defs.optiongroup):
        """Options relating to the caret and selection"""
                     
        class caret_colour(defs.option):
            """The colour of the caret."""
            default = '#000000'
            rtype = types.color
        class highlight_current_line(defs.option):
            """Whether the current line will e highlighted"""
            default = True
            rtype = types.boolean
        class current_line_color(defs.option):
            """The color that will be used to highligh the current line"""
            default = '#f0f0f0'
            rtype = types.color
        class selection_color(defs.option):
            """The background colour of the selection."""
            default = '#fefe90'
            rtype = types.color

    class edge_line(defs.optiongroup):
        """The line that appears at a set column width"""
        class show_edge_line(defs.option):
            """Whether the edge line will be shown."""
            rtype = types.boolean
            default = True
        class position(defs.option):
            """The character position of the line"""
            rtype = types.intrange(0, 240, 1)
            default = 78
        class color(defs.option):
            """The color of the edge line"""
            rtype = types.color
            default = '#909090'

class ScintillaEditor(service.service):    

    display_name = 'Pscyntilla Text Editor'
    config_definition = ScintillaConf

    class EditorView(defs.View):
        book_name = 'edit'
        view_type = ScintillaView
        
    def init(self):
        self._documents = {}
        self._views = {}
        self._current = None
    
    def reset(self):
        self._bind_document_actions()
        for view in self._views.values():
            view.optionize()
    
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
        self._current.editor.goto_line(linenumber + 1)
 
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
