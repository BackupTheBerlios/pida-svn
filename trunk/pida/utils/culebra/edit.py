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

try:
    from svbase import BaseView
except ImportError:
    from tvbase import BaseView

from replacebar import ReplaceBar
from searchbar import SearchBar
from buffers import CulebraBuffer
from common import KEY_ESCAPE, ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD


def _teardown_view(widget):
    widget.set_action_group(None)
    import weakref
    ref = weakref.ref(widget.search_bar)
    delattr(widget, "search_bar")
    assert ref() is None
    delattr(widget, "replace_bar")

class CulebraView(BaseView):
    def __init__(self, action_group):
        super(CulebraView, self).__init__()
        self.search_bar = SearchBar(self, action_group)
        self.replace_bar = ReplaceBar(self, self.search_bar, action_group)
        self.set_action_group(action_group)
        self.connect("destroy-event", _teardown_view)
    
    def set_action_group(self, action_group):
        self.search_bar.set_action_group(action_group)
        self.replace_bar.set_action_group(action_group)
    
    def set_background_color(self, color):
        self.modify_base(gtk.STATE_NORMAL, color)
    
    def set_font_color(self, color):
        self.modify_text(gtk.STATE_NORMAL, color)

    def set_font(self, fontstring):
        font_desc = pango.FontDescription(fontstring)
        if font_desc is not None:
            self.modify_font(font_desc)
    
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
        buff.get_file_ops().load()
    view.set_buffer(buff)
    
    return view


def main():
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = None
    win = gtk.Window()
    editor = create_editor(filename, None)
    editor.show()
    win.add(editor)
    win.show()
    win.connect("delete-event", gtk.main_quit)
    gtk.main()
    win.destroy()

if __name__ == '__main__':
    main()
