import scintilla
import mimetypes
from pida.utils.culebra.buffers import SafeFileWrite
from keyword import kwlist
import gobject
import gtk

# !
import sre
seps = r'[.\W]'
word_re = sre.compile(r'(\w+)$')

class Scintilla(scintilla.Scintilla):

    def get_text(self):
        return super(Scintilla, self).get_text(self.get_length() + 1)[1]

    def append_text(self, text):
        super(Scintilla, self).append_text(len(text), text)
    
    def get_line(self, number):
        return super(Scintilla, self).get_line(number)[1]

class Pscyntilla(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)
        self._sc = Scintilla()
        self._setup()
        self.filename = None

    def _setup(self):
        self._setup_margins()
        self._sc.connect('key', self.cb_unhandled_key)
        self._sc.connect('char-added', self.cb_char)

    def _setup_margins(self):
        self._sc.set_margin_type_n(0, scintilla.SC_MARGIN_NUMBER)
        self._sc.set_margin_type_n(2, scintilla.SC_MARGIN_SYMBOL)
        self._sc.set_margin_mask_n(2, scintilla.SC_MASK_FOLDERS)
        self._sc.set_property("tab.timmy.whinge.level", "1")
        self._sc.set_property("fold.comment.python", "0")
        self._sc.set_property("fold.quotes.python", "0")
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

    def get_is_modified(self):
        return self._sc.get_modify() != 0

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
        # XXX: visible is not used, why?
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

    def set_font_name(self, font_name):
        self.set_style(scintilla.STYLE_DEFAULT, font=font_name)
    
    def set_font_size(self, font_size):
        self.set_style(scintilla.STYLE_DEFAULT, size=font_size)
    
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
        self._sc.set_code_page(scintilla.SC_CP_UTF8)
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
    
    def revert(self):
        if self.filename is not None:
            self._sc.clear_all()
            self.load_file(self.filename)

    def can_undo(self):
        return self._sc.can_undo()

    def can_redo(self):
        return self._sc.can_redo()

    def can_paste(self):
        return self._sc.can_paste()

    def save(self):
        """Saves the current buffer to the file"""
        assert getattr(self, "filename", None) is not None
        fd = SafeFileWrite(self.filename)
        fd.write(self._sc.get_text())
        fd.close()
        self._sc.set_save_point()
        self.service.boss.call_command('buffermanager',
            'reset_current_document')

    def load_fd(self, fd):
        for line in fd:
            self._sc.append_text(line)
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

    def auto_complete(self):
        pos =  self._sc.get_current_pos()
        wpos = self._sc.word_start_position(pos, True)
        linepos, line = self._sc.get_cur_line()
        word = line[linepos - (pos - wpos):linepos]
        if word:
            pattern = sre.compile(r'\W(%s.+?)\W' % word)
            text = self._sc.get_text()
            words = set(pattern.findall(text))
            self._sc.auto_c_set_choose_single(True)
            self._sc.auto_c_set_drop_rest_of_word(True)
            self._sc.auto_c_show(len(word), ' '.join(sorted(list(words))))


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
            #TODO: emit a saved event
            self.save()
        elif args == (78, 2): # ctrl-n
            self.auto_complete()

    def cb_char(self, scint, ch):
        if ch in [10, 13]:
            pos =  self._sc.get_current_pos()
            i = self._sc.line_from_position(pos)
            text = self._sc.get_line(i - 1)

            for c in text:
                if c in '\t ':
                    self._sc.insert_text(pos, c)
                    pos = pos + 1
                    self._sc.goto_pos(pos)
                else:
                    break

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


