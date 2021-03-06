import scintilla
import mimetypes
from pida.utils.culebra.buffers import SafeFileWrite
from keyword import kwlist
from pida.utils.kiwiutils import gsignal
import gobject
import gtk

LEXERS = {
    "application/x-sh": "bash",
    "application/x-ruby": "ruby",
    "text/css": "css",
    "text/html": "html",
    "text/x-ada": "ada",
    "text/x-asm": "asm",
    "text/x-basic": "basic",
    "text/x-c++src": "cpp",
    "text/x-c++hdr": "cpp",
    "text/x-csrc": "cpp",
    "text/x-chdr": "cpp",
    "text/x-eiffel": "eiffel",
    "text/x-forth-source": "forth",
    "text/x-forth-script": "forth",
    "text/x-fortran": "fortran",
    "text/x-haskell": "haskell",
    "text/x-java": "java",
    "text/x-pascal": "pascal",
    "text/x-perl": "perl",
    "text/x-python": "python",
    "text/x-ruby": "ruby",
    "text/x-scheme": "lisp",
    "text/x-sh": "bash",
    "text/x-sql": "sql",
    "text/x-tex": ".tex",
    # made by me
    "text/x-ocaml": "caml",
    "text/x-apache-conf": "conf",
    "text/x-yaml": "yaml",
}
# TODO: move this onto documents? this is relevant to scintila, since
# it makes sure the needed mimetypes are installed
# see also: http://projects.edgewall.com/trac/browser/tags/trac-0.8.4/trac/Mimeview.py
# and http://projects.edgewall.com/trac/browser/trunk/trac/mimeview/enscript.py
MIMETYPES = (
    ("text/x-ada", ".ada"),
    ("text/x-asm", ".asm"),
    ("text/x-sh", ".sh"),
    ("text/x-basic", ".bas"),
    ("text/x-csrc", ".c"),
    ("text/x-chdr", ".h"),
    ("text/x-c++src", ".cpp"),
    ("text/x-c++src", ".cxx"),
    ("text/x-c++hdr", ".hpp"),
    ("text/x-c++hdr", ".hxx"),
    ("text/css", ".css"),
    ("text/x-scheme", ".scm"),
    ("text/x-haskell", ".hs"),
    ("text/x-sql", ".sql"),
    ("text/x-python", ".py"),
    ("text/x-python", ".pyw"),
    ("text/x-pascal", ".pas"),
    ("text/x-eiffel", ".e"),
    ("text/x-forth-source", ".fs"),
    ("text/x-forth-script", ".fth"),
    ("text/x-forth-script", ".4th"),
    ("text/x-fortran", ".f"),
    ("text/x-fortran", ".f77"),
    ("text/x-fortran", ".f90"),
    ("text/x-fortran", ".for"),
    ("text/x-fortran", ".f95"),
    ("text/x-fortran", ".fpp"),
    ("text/x-fortran", ".ftn"),
    ("text/x-perl", ".pl"),
    ("text/x-ruby", ".rb"),
    ("text/x-tex", ".tex"),
    # this was created by me in order for it to be picked up later
    ("text/x-ocaml", ".ml"),
    ("text/x-apache-conf", ".conf"),
    ("text/x-lua", ".lua"),
    ("text/x-yaml", ".yml"),
)
for key, val in MIMETYPES:
    mimetypes.add_type(key, val)

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

    gsignal('mark-clicked', gobject.TYPE_INT, gobject.TYPE_BOOLEAN)

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
        # bp margin and marker
        self._sc.set_margin_type_n(1, scintilla.SC_MARGIN_SYMBOL)
        self._sc.set_margin_width_n(1, 14)
        self._sc.set_margin_sensitive_n(1, True)
        self._sc.set_margin_mask_n(1, ~scintilla.SC_MASK_FOLDERS)
        self._sc.marker_define(1, scintilla.SC_MARK_SMALLRECT)
        self._sc.marker_set_back(1, self._sc_colour('#900000'))
        self._sc.marker_set_fore(1, self._sc_colour('#900000'))
        # folding markers
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

    def set_currentline_visible(self, visible):
        self._sc.set_caret_line_visible(visible)

    def set_currentline_color(self, color):
        self._sc.set_caret_line_back(self._sc_colour(color))

    def set_edge_column_visible(self, visible, size):
        self._sc.set_edge_mode((visible and scintilla.EDGE_LINE) or 
            scintilla.EDGE_NONE)
        self._sc.set_edge_column(size)
    
    def set_edge_color(self, color):
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
        
        try:
            ftype = LEXERS[mimetype]
            self._sc.set_lexer_language(ftype)
            if ftype == 'python':
                self._sc.set_key_words(0, ' '.join(kwlist))
                
        except KeyError:
            pass
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
        elif margin == 1:
            # bp margin
            line = self._sc.line_from_position(pos)
            marker = self._sc.marker_get(line)
            self.emit('mark-clicked', line, marker & 2)

    def show_mark(self, line):
        self._sc.marker_add(line, 1)

    def hide_mark(self, line):
        self._sc.marker_delete(line, 1)

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
        update_style_from_schema(self, COLOR_SCHEMA, DARK)
        return
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
        update_style_from_schema(self, COLOR_SCHEMA, NATIVE)
        return
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

    def set_color_schema(self, schema):
        update_style_from_schema(self, COLOR_SCHEMA, schema)


COLOR_SCHEMA = {
    "base": (0, 11, 12),
    "comments": (1,),
    "numbers": (2,),
    "strings": (3, 4, 13),
    "multi line strings": (7,),
    "keywords": (5, 6),
    "class names": (8,),
    "symbols": (10,),
    "function names": (9,)
}

NATIVE = {
    "base": dict(fore="#000000", back='#fafafa'),
    "comments": dict(fore="#999999", italic=True),
    "numbers": dict(fore="#009000"),
    "multi line strings": dict(fore='#909000'),
    "strings": dict(fore="#900090"),
    "keywords": dict(fore="#000090", bold=True),
    "class names": dict(fore="#009090", bold=True),
    "symbols": dict(fore="#000000"),
    "function names": dict(fore="#900000"),
    "caret": dict(fore='#000000', back='#f0f0f0'),
    "selection": dict(back='#f0f0a0')
}

DARK = {
    "base": dict(fore='#f0f0f0', back='#000033'),
    "comments": dict(fore='#a0a0a0'),
    "numbers": dict(fore='#00f000'),
    "strings": dict(fore='#a0a000'),
    "multi line strings": dict(fore="#ed9d13"),
    "keywords": dict(fore='#9090ff'),
    "symbols": dict(fore='#00f0f0'),
    "class names": dict(fore='#90ff90', bold=True),
    "function names": dict(fore='#90ff90', bold=True),
    "caret": dict(fore='#ff0000', back='#222244'),
    "selection": dict(back='#333355')
}

DGREEN = {
    "base": dict(fore='#c0f0c0', back='#003300'),
    "comments": dict(fore='#a09090'),
    "numbers": dict(fore='#00f000'),
    "strings": dict(fore='#a0a000'),
    "multi line strings": dict(fore="#ed9d13"),
    "keywords": dict(fore='#90ffff'),
    "symbols": dict(fore='#00f0c0'),
    "class names": dict(fore='#90ff90', bold=True),
    "function names": dict(fore='#90ff90', bold=True),
    "caret": dict(fore='#ff0000', back='#224422'),
    "selection": dict(back='#335533')
}

ALI_THEME = {
    "base": dict(fore='#f0f0f0', back='#000033'),
    "comments": dict(fore='#a0a0a0'),
    "numbers": dict(fore='#00f000'),
    "strings": dict(fore='#c0c0ff'),
    "multi line strings": dict(fore="#c09090"),
    "keywords": dict(fore='#f0c0a0'),
    "symbols": dict(fore='#f09000'),
    "class names": dict(fore='#ffff90', bold=True),
    "function names": dict(fore='#90ff90', bold=True),
    "caret": dict(fore='#ff0000', back='#222244'),
    "selection": dict(back='#333355')
}

TIAGO_THEME = {
    "base": dict(fore="#000000", back='#fafafa'),
    "comments": dict(fore="#999999", italic=True),
    "numbers": dict(fore="#3677a9"),
    "multi line strings": dict(fore='#a0a000'),
    "strings": dict(fore="#ed9d13"),
    "keywords": dict(fore="#6ab825", bold=True),
    "class names": dict(fore="#900000", bold=True),
    "symbols": dict(fore="#909090"),
    "function names": dict(fore="#447fcf"),
    "caret": dict(fore='#000000', back='#f0f0f0'),
    "selection": dict(back='#f0f0a0')
}

THEMES = {'Dark': DARK,
          'Light': NATIVE,
          'Dark Green': DGREEN,
          'Tiago': TIAGO_THEME,
          'Ali Special': ALI_THEME}

def update_style_from_schema(sci, schema, style):
    base = style["base"]
    comm = style["comments"]
    caret = style['caret']
    select = style['selection']
    sci.set_background_color(base["back"])
    sci.set_edge_color(comm['fore'])
    sci.set_caret_colour(caret.get('fore', base['fore']))
    sci.set_currentline_color(caret['back'])
    sci.set_selection_color(select['back'])
    sci.set_foldmargin_colours(comm["fore"], comm.get("back", base["back"]))
    sci.set_linenumber_margin_colours(comm["fore"], comm.get("back", base["back"]))
    for key, vals in schema.iteritems():
        for style_id in vals:
            curr_style = style[key]
            sci.set_style(style_id, **curr_style)

