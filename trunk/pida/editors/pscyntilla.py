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
from pida.core import actions, errors
from pida.core import service
from pida.utils.pscyntilla import Pscyntilla, THEMES
from pida.model import attrtypes as types
defs = service.definitions

def parse_fontdesc(fontdesc):
    """Returns the name and size"""
    name, size = fontdesc.rsplit(' ', 1)
    size = int(size)
    return name, size

class ScintillaView(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_TITLE = False

    def init(self):
        self.editor = Pscyntilla()
        self.marks = {}
        # TODO: need a better way to do this:
        self.editor.service = self.service
        self.widget.pack_start(self.editor._sc)
        self.optionize()
        self.editor._sc.connect('modified', self.cb_modified)
        self.editor._sc.connect('save-point-reached', self.cb_save_point_reached)
        self.editor._sc.connect('save-point-left', self.cb_save_point_left)
        self.editor.connect('mark-clicked', self.cb_mark_clicked)

    def cb_save_point_reached(self, editor, *args):
        self.service._save_act.set_sensitive(False)
        self.service._revert_act.set_sensitive(False)
    
    def cb_save_point_left(self, editor, *args):
        self.service._save_act.set_sensitive(True)
        self.service._revert_act.set_sensitive(True)
    
    def cb_mark_clicked(self, ed, line, hasmark):
        if self.editor.filename:
            if hasmark:
                cmd = 'del_breakpoint'
                self.service.boss.call_command('pythondebugger', cmd,
                    index=self.marks[line])
            else:
                cmd = 'set_breakpoint'
                # line + 1 debugger starts at line 1
                self.service.boss.call_command('pythondebugger', cmd,
                    filename=self.editor.filename, line=line + 1)
    
    def optionize(self):
        """Loads the user options"""
        opts = self.service.opts
        options = self.service.options
        editor = self.editor
        
        # font
        font = options.font
        print opts.font__size, opts.font__name, opts.font__font
        editor.set_font_size(opts.font__size)
        editor.set_font_name(opts.font__name)
        
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
        
        # line numbers
        line_numbers = options.line_numbers
        editor.set_linenumbers_visible(line_numbers.show_line_numbers)

        # caret and currentline
        caret = options.caret
        highlight = caret.highlight_current_line
        editor.set_currentline_visible(highlight)

        # edge column
        edge_line = options.edge_line
        editor.set_edge_column_visible(edge_line.show_edge_line,
                                       edge_line.position)
        
        # color options
        editor.set_color_schema(THEMES[options.colors.scheme])
            

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
        label = 'Font'
        class font:
            """The font used in the editor"""
            rtype = types.font
            label = "Font:"
            default = 'Monospace 12'
        
        class name:
            rtype = types.readonly
            hidden = True
            dependents = ("font__font",)

            def fget(self):
                return self.font__font.rsplit(" ", 1)[0]
        
        class size:
            rtype = types.readonly
            hidden = True
            label = 'Size'
            dependents = ("font__font",)
            
            def fget(self):
                return int(self.font__font.rsplit(" ", 1)[1])
                
    class indenting(defs.optiongroup):
        """Indenting options"""
        label = 'Indenting'
        __order__ = ['use_tabs', 'space_indent_width', 'tab_width']
        class use_tabs(defs.option):
            """Use tabs for indenting"""
            rtype = types.boolean
            default = False
            label = 'Use tabs'
        
        class tab_width(defs.option):
            """Width of tabs"""
            rtype = types.intrange(1, 16, 1)
            default = 4
            label = 'Tab width'
        
        class space_indent_width(defs.option):
            """With of space indents, if not using tabs."""
            rtype = types.intrange(1, 16, 1)
            default = 4
            label = 'Number of spaces per indent'
    
    class line_numbers(defs.optiongroup):
        """Options relating to line numbers and the line number margin."""
        label = 'Line numbers'
        class show_line_numbers(defs.option):
            """Whether line numbers will be shown."""
            rtype = types.boolean
            default = True
            label = 'Show line numbers'

    class colors(defs.optiongroup):
        """Options for colours."""
        label = 'Theme'
   
        class scheme:
            """The Color scheme that will be used"""
            rtype = types.stringlist(*THEMES.keys())
            default = 'Light'
            label = 'Color scheme'

    class folding(defs.optiongroup):
        """Options relating to code folding"""
        label = 'Folding'
        class use_folding(defs.option):
            """Use folding"""
            rtype = types.boolean
            default = True
            label = 'Use Folding'
        class marker_size(defs.option):
            """Marker size"""
            rtype = types.intrange(8, 32, 1)
            default = 14
            sensitive_attr = 'folding__use_folding'
            label = 'Fold margin width'
      

    class caret(defs.optiongroup):
        """Options relating to the caret and selection"""
        label = 'Caret'
    
        class highlight_current_line(defs.option):
            """Whether the current line will e highlighted"""
            default = True
            rtype = types.boolean
            label = 'Highlight current line'
   

    class edge_line(defs.optiongroup):
        """The line that appears at a set column width"""
        label = 'Edge'
        class show_edge_line(defs.option):
            """Whether the edge line will be shown."""
            rtype = types.boolean
            default = True
            label = 'Show edge marker line'
        class position(defs.option):
            """The character position of the line"""
            rtype = types.intrange(0, 240, 1)
            default = 78
            sensitive_attr = 'edge_line__show_edge_line'
            label = 'Edge marker position'
     

class DispatchMethod:
    def __init__(self, elements, attr):
        self.__elements = elements
        self.__attr = attr
    
    def __call__(self, *args, **kwargs):
        views = self.__elements
        attr = self.__attr
        return [getattr(view.editor, attr)(*args, **kwargs) for view in views]
    
    def __repr__(self):
        return "<foreach %r>.%s()" % (self.__elements, self.__attr)

class Dispatcher:
    def __init__(self, elements):
        self.__elements = elements
    
    def __getattr__(self, attr):
        return DispatchMethod(self.__elements, attr)
    
    def __repr__(self):
        return "<foreach %r>" % self.__elements

class ScintillaEditor(service.service):    

    display_name = 'Pscyntilla Text Editor'
    config_definition = ScintillaConf

    class EditorView(defs.View):
        book_name = 'edit'
        view_type = ScintillaView
    
    _views = {}
    
    def init(self):
        self._documents = {}
        self._views = {}
        self._current = None
        self._marks = {}
    
    views = property(lambda self: self._views.itervalues())
    
    foreach_editor = property(lambda self: Dispatcher(self.views))
    
    def reset(self):
        self._bind_document_actions()
        for view in self._views.values():
            view.optionize()
    
    def cb_colors__scheme(self, scheme):
        self.foreach_editor.set_color_schema(THEMES[scheme])
    
    def cb_caret__highlight_current_line(self, high):
        self.foreach_editor.set_currentline_visible(high)

    def cb_font__size(self, size):
        self.foreach_editor.set_font_size(size)
    
    def cb_font__name(self, name):
        self.foreach_editor.set_font_name(name)
    
    def cb_indenting__use_tabs(self, use_tabs):
        self.foreach_editor.set_use_tabs(use_tabs)

    def cb_indenting__tab_width(self, tab_width):
        self.foreach_editor.set_tab_width(tab_width)
    
    def cb_indenting__space_indent_width(self, space_indent_width):
        if self.opts.indenting__use_tabs:
            editors = self.foreach_editor
            editors.set_spaceindent_width(space_indent_width)
    
    def cb_line_numbers__show_line_numbers(self, show):
        self.foreach_editor.set_linenumbers_visible(show)
    
    # folding options
    def cb_folding__use_folding(self, use):
        width = self.opts.folding__marker_size
        self.foreach_editor.use_folding(use, width)
    
    def cb_folding__marker_size(self, size):
        use = self.opts.folding__use_folding
        self.foreach_editor.use_folding(use, width=size)
    
    # not used
    def _cb_folding__marker_background(self, back):
        fore = self.opts.folding__marker_foreground
        self.foreach_editor.set_foldmargin_colours(back=back, fore=fore)
      
    # edge column options
    def cb_edge_line__show_edge_line(self, show):
        self._config_edge_line()
        
    def cb_edge_line__position(self, position):
        self._config_edge_line()
    
    def _config_edge_line(self):
        self.foreach_editor.set_edge_column_visible(
            self.opts.edge_line__show_edge_line,
            self.opts.edge_line__position)
        
    def cmd_start(self):
        self.get_service('editormanager').events.emit('started')

    def cmd_edit(self, document=None):
        if document.unique_id not in self._views:
            try:
                self._load_document(document)
            except TypeError:
                raise errors.BadDocument('Pscyntilla cannot open this file. '
                                         'Is it binary?')
        self._view_document(document)

    def cmd_save(self):
        self._current.editor.save()
    
    def cmd_revert(self):
        self._current.editor.revert()
   
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
    
    def cmd_show_mark(self, index, filename, line):
        for doc in self._documents.values():
            if doc.filename == filename:
                v = self._views[doc.unique_id]
                v.editor.show_mark(line)
                v.marks[line] = index
                def hide(line=line):
                    v.editor.hide_mark(line)
                    del v.marks[line]
                self._marks[index] = hide
    
    def cmd_hide_mark(self, index):
        print index
        try:
            self._marks[index]()
        except KeyError:
            raise
    
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
