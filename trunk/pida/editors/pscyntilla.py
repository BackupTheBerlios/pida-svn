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

import scintilla
import mimetypes
from pida.utils.culebra.buffers import SafeFileWrite
from keyword import kwlist
import gobject
from pida.utils.kiwiutils import gsignal, gproperty

defs = service.definitions
types = service.types


class Pscyntilla(gobject.GObject):

    def __init__(self):
        self._sc = scintilla.Scintilla()
        self._setup()

    def _setup(self):
        self._setup_margins()
        self._sc.connect('key', self.cb_unhandled_key)

    def _setup_margins(self):
        self._sc.set_margin_type_n(0, scintilla.SC_MARGIN_NUMBER)
        self._sc.set_margin_type_n(2, scintilla.SC_MARGIN_SYMBOL)
        self._sc.set_margin_mask_n(2, scintilla.SC_MASK_FOLDERS)
        self._sc.set_property("tab.timmy.whinge.level", "1")
        self._sc.set_property("fold.comment.python", "0")
        self._sc.set_property("fold.quotes.python", "0")
        #self._sc.set_fold_margin_colour(True, self.colour_from_string('300000'))
        #self._sc.set_fold_margin_hi_colour(True, self.colour_from_string('300000'))
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDEREND,
                           scintilla.SC_MARK_BOXPLUSCONNECTED)
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDEROPENMID,
                           scintilla.SC_MARK_BOXMINUSCONNECTED)
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDERMIDTAIL,
                           scintilla.SC_MARK_TCORNER)
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDERTAIL,
                           scintilla.SC_MARK_LCORNER)
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDERSUB,
                           scintilla.SC_MARK_VLINE)
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDER,
                           scintilla.SC_MARK_BOXPLUS)
        self._sc.marker_define(scintilla.SC_MARKNUM_FOLDEROPEN,
                           scintilla.SC_MARK_BOXMINUS)
        self._sc.connect('margin-click', self.cb_margin_click)

    def goto_line(self, linenumber):
        self._sc.goto_line(linenumber - 1)
        wanted = linenumber - (self._sc.lines_on_screen() / 2)
        actual = self._sc.get_first_visible_line()
        self._sc.line_scroll(0, wanted - actual)
        self._sc.grab_focus()

    def set_caret_colour(self, colour):
        self._sc.set_caret_fore(self._sc_colour(colour))

    def set_caret_line_visible(self, visible, colour=None):
        self._sc.set_caret_line_visible(visible)
        if colour is not None:
            self._sc.set_caret_line_back(self._sc_colour(colour))

    def set_edge_column_visible(self, visible, size, color):
        self._sc.set_edge_mode(scintilla.EDGE_LINE)
        self._sc.set_edge_column(size)
        self._sc.set_edge_colour(self._sc_colour(color))

    def set_use_tabs(self, use_tabs):
        self._sc.set_use_tabs(use_tabs)

    def set_tab_width(self, tab_width):
        self._sc.set_tab_width(tab_width)

    def set_spaceindent_width(self, si_width):
        self._sc.set_indent(si_width)

    def set_linenumbers_visible(self, visible, width=32):
        if not visible:
            width = 0
        self._sc.set_margin_width_n(0, width)

    def use_folding(self, use, width=14, show_line=True):
        if use:
            self._sc.set_property('fold', '1')
            if show_line:
                self._sc.set_fold_flags(16)
        else:
            width = 0
            self._sc.set_property('fold', '0')
        self._sc.set_margin_width_n(2, width)
        self._sc.set_margin_sensitive_n(2, use)

    def set_foldmargin_colours(self, fore, back):
        b = self._sc_colour(back)
        f = self._sc_colour(fore)
        self._sc.set_fold_margin_colour(True, b)
        self._sc.set_fold_margin_hi_colour(True, b)
        for i in range(25, 32):
            self._sc.marker_set_back(i, f)
            self._sc.marker_set_fore(i, b)
        self.set_style(scintilla.STYLE_DEFAULT, fore=fore)
        
    def set_style(self, number,
                        fore=None,
                        back=None,
                        bold=None,
                        font=None,
                        size=None,
                        italic=None):
        if fore is not None:
            self._sc.style_set_fore(number, self._sc_colour(fore))
        if back is not None:
            self._sc.style_set_back(number, self._sc_colour(back))
        if bold is not None:
            self._sc.style_set_bold(number, bold)
        if font is not None:
            self._sc.style_set_font(number, '!%s' % font)
        if size is not None:
            self._sc.style_set_size(number, size)
        if italic is not None:
            self._sc.style_set_italic(number, italic)

    def set_font(self, fontname, size):
        self.set_style(scintilla.STYLE_DEFAULT, font=fontname, size=size)

    def set_linenumber_margin_colours(self, foreground, background):
        self.set_style(scintilla.STYLE_LINENUMBER, fore=foreground,
                        back=background)
    
    def get_widget(self):
        return self._sc

    def _sc_colour(self, colorspec):
        c = gtk.gdk.color_parse(colorspec)
        return (c.red/256) | (c.green/256) << 8 | (c.blue/256) << 16

    def load_file(self, filename):
        self.filename = filename
        f = open(filename, 'r')
        mimetype, n = mimetypes.guess_type(filename)
        if mimetype:
            ftype = mimetype.split('/')[-1].split('-')[-1]
            self._sc.set_lexer_language(ftype)
            if ftype == 'python':
                self._sc.set_key_words(0, ' '.join(kwlist))
        self.load_fd(f)
        self._sc.empty_undo_buffer()
        self._sc.set_save_point()

    def grab_focus(self):
        self._sc.grab_focus()

    def cut(self):
        self._sc.cut()

    def copy(self):
        self._sc.copy()

    def paste(self):
        self._sc.paste()

    def undo(self):
        self._sc.undo()

    def redo(self):
        self._sc.redo()

    def can_undo(self):
        return self._sc.can_undo()

    def can_redo(self):
        return self._sc.can_redo()

    def can_paste(self):
        return self._sc.can_paste()

    def save(self):
        """Saves the current buffer to the file"""
        assert self.filename is not None
        fd = SafeFileWrite(self.filename)
        txt = self._sc.get_text(self._sc.get_length())[-1]
        fd.write(''.join(txt))
        fd.close()
        self._sc.set_save_point()

    def load_fd(self, fd):
        for line in fd:
            self._sc.append_text(len(line), line)
        self._sc.colourise(0, -1)

    def get_all_fold_headers(self):
        for i in xrange(self._sc.get_line_count()):
            level = self._sc.get_fold_level(i)
            if level & scintilla.SC_FOLDLEVELHEADERFLAG:
                yield i, level
    
    def get_toplevel_fold_headers(self):
        for i, level in self.get_all_fold_headers():
            if level & scintilla.SC_FOLDLEVELNUMBERMASK == 1024:
                yield i
    
    def collapse_all(self):
        for i in self.get_toplevel_fold_headers():
            if self._sc.get_fold_expanded(i):
                self._sc.toggle_fold(i)
    
    def expand_all(self):
        for i in self.get_toplevel_fold_headers():
            if not self._sc.get_fold_expanded(i):
                self._sc.toggle_fold(i)
   
    def cb_margin_click(self, ed, mod, pos, margin):
        if margin == 2:
            if mod == 1:
                self.collapse_all()
            elif mod == 6:
                self.expand_all()
            else:
                line = self._sc.line_from_position(pos)
                if (self._sc.get_fold_level(line) &
                    scintilla.SC_FOLDLEVELHEADERFLAG):
                    self._sc.toggle_fold(line)

    def cb_unhandled_key(self, widg, *args):
        if args == (122, 4):
            i = self._sc.line_from_position(self._sc.get_current_pos())
            self._sc.toggle_fold(i)
        elif args == (83, 2):
            self.save()
            #TODO: emit a saved event

    def set_background_color(self, back):
        self.set_style(scintilla.STYLE_DEFAULT,
                       back=back)
        for i in range(32):
            self.set_style(i, back=back)

    def set_selection_color(self, color):
        self._sc.set_sel_back(True, self._sc_colour(color))

    def use_dark_theme(self):
        self.set_background_color('#000033')
        self.set_style(0, fore='#f0f0f0')
        self.set_style(1, fore='#a0a0a0')
        self.set_style(2, fore='#00f000')
        self.set_style(3, fore='#c000c0')
        self.set_style(4, fore='#c000c0')
        self.set_style(5, fore='#6060fa')
        self.set_style(6, fore='#c0c000')
        self.set_style(7, fore='#c0c000')
        self.set_style(8, fore='#00f000', bold=True)
        self.set_style(9, fore='#f0a000', bold=True)
        self.set_style(10, fore='#00f0f0')
        self.set_style(11, fore='#f0f0f0')
        self.set_style(12, fore='#a0a0a0')

    def use_light_theme(self):
        self.set_background_color('#fafafa')
        # base
        self.set_style(0, fore='#000000')
        # comments
        self.set_style(1, fore='#909090')
        # numbers
        self.set_style(2, fore='#00a000')
        # dq strings
        self.set_style(3, fore='#600060')
        # sq strings
        self.set_style(4, fore='#600060')
        # keywords
        self.set_style(5, fore='#0000a0')
        self.set_style(6, fore='#00c000')
        # docstring
        self.set_style(7, fore='#a0a000')
        # class names
        self.set_style(8, fore='#009000')
        # func names
        self.set_style(9, fore='#a05000')
        # symbols
        self.set_style(10, fore='#c00000')
        # base
        self.set_style(11, fore='#000000')
        self.set_style(12, fore='#0000a0')


class ScintillaView(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_TITLE = False

    def init(self):
        #sw = gtk.ScrolledWindow()
        #self.widget.pack_start(sw)
        #sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.editor = Pscyntilla()
        #sw.add(self.editor)
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

        print 'savepointleave'    
        
    def optionize(self):
        opt = self.service.opt
        # font
        self.editor.set_font(
                *self._font_and_size(opt('font', 'font')))
        # indenting options
        use_tabs = opt('indenting', 'use_tabs')
        self.editor.set_use_tabs(use_tabs)
        self.editor.set_tab_width(opt('indenting', 'tab_width'))
        if not use_tabs:
            self.editor.set_spaceindent_width(
                opt('indenting', 'space_indent_width'))
        # folding options
        self.editor.use_folding(
            opt('folding', 'use_folding'), width=opt('folding', 'marker_size'))
        self.editor.set_foldmargin_colours(
            back=opt('folding', 'marker_background'),
            fore=opt('folding', 'marker_foreground'))
        # line numbers
        self.editor.set_linenumber_margin_colours(
            background=opt('line_numbers', 'background'),
            foreground=opt('line_numbers', 'foreground'))
        self.editor.set_linenumbers_visible(
            opt('line_numbers', 'show_line_numbers'))
        if opt('colors', 'use_dark_theme'):
            self.editor.use_dark_theme()
        else:
            self.editor.use_light_theme()
        # caret and selection
        car = 'caret'
        self.editor.set_caret_colour(opt(car, 'caret_colour'))
        self.editor.set_caret_line_visible(
            opt(car, 'highlight_current_line'),
            opt(car, 'current_line_color'))
        self.editor.set_selection_color(
            opt(car, 'selection_color'))
        # edge column
        el = 'edge_line'
        self.editor.set_edge_column_visible(
            opt(el, 'show_edge_line'),
            opt(el, 'position'),
            opt(el, 'color'))

    def _font_and_size(self, fontdesc):
        name, size = fontdesc.rsplit(' ', 1)
        size = int(size)
        return name, size
        
    def cb_modified(self, editor, *args):
        if self.service._current:
            self.service._sensitise_actions()
      

class ScintillaEditor(service.service):    

    display_name = 'Pscyntilla Text Editor'

    class EditorView(defs.View):
        book_name = 'edit'
        view_type = ScintillaView

    class font(defs.optiongroup):
        """The font used in the editor"""
        class font(defs.option):
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
            rtype = types.boolean
            default = True
        class marker_size(defs.option):
            rtype = types.intrange(8, 32, 1)
            default = 14
        class marker_background(defs.option):
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
