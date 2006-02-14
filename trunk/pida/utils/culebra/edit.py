# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = (
    "2005-2006, Tiago Cogumbreiro "
    "2005, Fernando San Martín Woerner"
)

__author__ = (
    "Tiago Cogumbreiro <cogumbreiro@users.sf.net>",
    "Fernando San Martín Woerner <fsmw@gnome.org>",
    
)

import gtk
import pango
import gtksourceview
from rat.text import make_source_view_indentable

from replacebar import ReplaceBar
from searchbar import SearchBar
from buffers import CulebraBuffer
from common import KEY_ESCAPE, ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD


class CulebraView(gtksourceview.SourceView):
    def __init__(self, action_group):
        gtksourceview.SourceView.__init__(self)
            
        self.set_auto_indent(True)
        self.set_show_line_numbers(True)
        self.set_show_line_markers(True)
        self.set_tabs_width(4)
        self.set_margin(80)
        self.set_show_margin(True)
        self.set_smart_home_end(True)
        self.set_highlight_current_line(True)
        self.set_insert_spaces_instead_of_tabs(True)
        font_desc = pango.FontDescription('monospace 10')
        if font_desc is not None:
            self.modify_font(font_desc)
        
        self.search_bar = SearchBar(self, action_group)
        self.replace_bar = ReplaceBar(self, self.search_bar, action_group)
        self.set_action_group(action_group)
        make_source_view_indentable(self)
    
    def set_action_group(self, action_group):
        self.search_bar.set_action_group(action_group)
        self.replace_bar.set_action_group(action_group)
    
    def set_background_color(self, color):
        self.modify_base(gtk.STATE_NORMAL, color)
    
    def set_font_color(self, color):
        self.modify_text(gtk.STATE_NORMAL, color)
    
    def set_buffer(self, buff):
        self.replace_bar.set_buffer(buff)
        self.search_bar.set_buffer(buff)
        super(CulebraView, self).set_buffer(buff)
    
    def find(self, find_forward):
        buff = self.get_buffer()
        found = buff.search(find_forward=find_forward)
        self.focus_carret()
        return found

    def _on_key_pressed(self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.toggle_action.set_active(False)

    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
            self._widget.connect("key-release-event", self._on_key_pressed)

        
        return self._widget
    
    widget = property(get_widget)


    def focus_carret(self):
        buff = self.get_buffer()
        mark = buff.get_insert()
        line_iter = buff.get_iter_at_mark(mark)
        self.scroll_to_iter(line_iter, 0.25)

def create_widget(filename, action_group):

    vbox = gtk.VBox(spacing=12)
    vbox.show()

    scroller = gtk.ScrolledWindow()
    scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scroller.show()
    vbox.add(scroller)

    editor = create_editor(filename, action_group)
    editor.set_name("editor")
    editor.show()
    scroller.add(editor)
    
    vbox.pack_end(editor.replace_bar.widget, False, False)
    vbox.pack_end(editor.search_bar.widget, False, False)
    
    
    return vbox, editor


def create_editor(filename, action_group):
    view = CulebraView(action_group)
    # XXX: there's no way to select an encoding
    buff = CulebraBuffer(filename)
    if filename is not None:
        buff.load_from_file()
    view.set_buffer(buff)
    
    return view





