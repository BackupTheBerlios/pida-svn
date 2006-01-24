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
import gtk.gdk
import gobject
import sys, os
import pango
import gtksourceview
import gnomevfs
import weakref
import codecs

from events import *

from replacebar import ReplaceBar
from searchbar import SearchBar
from buffers import CulebraBuffer

from common import *
from gtkutil import *
BLOCK_SIZE = 2048


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
        action_group.get_action(ACTION_FIND_FORWARD).connect("activate", self.on_find_forward)
        action_group.get_action(ACTION_FIND_BACKWARD).connect("activate", self.on_find_backwards)
        make_source_view_indentable(self)
    
    def set_background_color(self, color):
        self.modify_base(gtk.STATE_NORMAL, color)
    
    def set_buffer(self, buff):
        self.replace_bar.set_buffer(buff)
        self.search_bar.set_buffer(buff)
        super(CulebraView, self).set_buffer(buff)
    
    def find(self, find_forward):
        buff = self.get_buffer()
        found = buff.search(find_forward=find_forward)

        if not found and len(buff.get_selection_bounds()) == 0:
            found = buff.search(find_forward=not find_forward)

        if not found:
            return
            
        mark = buff.get_insert()
        line_iter = buff.get_iter_at_mark(mark)
        self.scroll_to_iter(line_iter, 0.25)

    def on_find_forward(self, action):
        self.find(True)
    
    def on_find_backwards(self, action):
        self.find(False)

    def on_key_pressed(self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.toggle_action.set_active(False)

    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
            self._widget.connect("key-release-event", self.on_key_pressed)

        
        return self._widget
    
    widget = property(get_widget)



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


# XXX: move this to CulebraBuffer class?
def load_buffer(filename, buff=None):
    """
    Creates a CulebraBuffer from a filename
    """
    new_entry = True
    if buff is None:
        buff = CulebraBuffer(filename=filename)
    # We only update the contents of a new buffer
    fd = open(filename)
    try:
        buff.begin_not_undoable_action()
        buff.set_text("")
        data = fd.read()
        enc_data = None
        for enc in(sys.getdefaultencoding(), "utf-8", "iso8859", "ascii"):
            try:
                enc_data = unicode(data, enc)
                buff.encoding = enc
                break
            except UnicodeDecodeError:
                pass
        assert enc_data is not None, "There was a problem detecting the encoding"
            
        
        buff.set_text(enc_data)
        buff.set_modified(False)
        buff.place_cursor(buff.get_start_iter())
        buff.end_not_undoable_action()

    finally:
        fd.close()

    return buff
    
            
def create_editor(filename, action_group):
    view = CulebraView(action_group)
    buff = load_buffer(filename)
    view.set_buffer(buff)
    
    
#    def on_foo(editor):
#        buff.search_text = "a"
#        buff.replace_text = "b"
#        buff.search()
#        buff.replace()
#        buff.replace_all()
#        editor.replace_toggle.activate()
        
#    gobject.timeout_add(100, on_foo, view)
#    gobject.timeout_add(4000, on_foo, view)
    return view





if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        fname = sys.argv[-1]
    else:
        fname = ""
    w = create_window(fname)
    w.connect("delete-event", gtk.main_quit)
    w.show()
    w.set_title("Culebra")
    gtk.main()
