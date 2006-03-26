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
import interfaces
try:
    from svbase import BaseView
except ImportError:
    from tvbase import BaseView

import replacebar
import searchbar
from buffers import BaseBuffer
import buffers
from common import *
#from common import create_dummy_action_group
import core

def _teardown_view(widget):
    widget.set_action_group(None)
    import weakref
    ref = weakref.ref(widget.search_bar)
    delattr(widget, "search_bar")
    assert ref() is None
    delattr(widget, "replace_bar")


def register_services(service_provider):
    services = ("view", interfaces.ICarretController,
                interfaces.ISelectColors, interfaces.ISelectFont)
                
    service_provider.register_factory(lambda service_provider: CulebraView(), base_service=False, *services)
    service_provider.register_factory(ActionGroupController, interfaces.IActionGroupController)
    
    # XXX: need a way to create a simple factory
    view = service_provider.get_service("view")
    service_provider.register_service(view.get_buffer(), "buffer")
    
    # Register other modules
    searchbar.register_services(service_provider)
    replacebar.register_services(service_provider)
    buffers.register_services(service_provider)

class ActionGroupController(core.BaseService):
    search = core.Depends(interfaces.ISearchBar)
    replace = core.Depends(interfaces.IReplaceBar)
    
    def set_action_group(self, action_group):
        self.search.set_action_group(action_group)
        self.replace.set_action_group(action_group)

class CulebraView(BaseView):
    
    def __init__(self):
        super(CulebraView, self).__init__()
        #super(CulebraView, self).set_buffer(CulebraBuffer())
        # Make sure we have a 
        super(CulebraView, self).set_buffer(BaseBuffer())
        self.connect("destroy-event", _teardown_view)
    
    
    def set_background_color(self, color):
        self.modify_base(gtk.STATE_NORMAL, color)
    
    def set_font_color(self, color):
        self.modify_text(gtk.STATE_NORMAL, color)

    def set_font(self, fontstring):
        font_desc = pango.FontDescription(fontstring)
        if font_desc is not None:
            self.modify_font(font_desc)

    def set_buffer(self, buff):
        raise AttributeError
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

#    def get_widget(self):
#        if self._widget is None:
#            self._widget = self.create_widget()
#            self._widget.connect("key-release-event", self._on_key_pressed)
#
#        
#        return self._widget
#    
#    widget = property(get_widget)


    def focus_carret(self):
        buff = self.get_buffer()
        mark = buff.get_insert()
        line_iter = buff.get_iter_at_mark(mark)
        self.scroll_to_iter(line_iter, 0.25)

    def goto_line(self, index):
        buff = self.get_buffer()
        # Get line iterator
        line_iter = buff.get_iter_at_line(index)
        # Move scroll to the line iterator
        self.scroll_to_iter(line_iter, 0.25)
        # Place the cursor at the begining of the line
        buff.place_cursor(line_iter)
        
def create_widget(filename, action_group):

    vbox = gtk.VBox(spacing=12)
    vbox.show()

    scroller = gtk.ScrolledWindow()
    scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scroller.show()
    vbox.add(scroller)
    
    provider = create_editor(filename, action_group)
    editor = provider.get_service("view")
    
    editor.set_name("editor")
    
    search_bar = provider.get_service(interfaces.ISearchBar)
    widget = search_bar.get_widget()
    widget.set_name("search_bar")

    replace_bar = provider.get_service(interfaces.IReplaceBar)
    widget = replace_bar.get_widget()
    widget.set_name("replace_bar")
    
    editor.show()
    scroller.add(editor)
    vbox.pack_end(replace_bar.widget, False, False)
    vbox.pack_end(search_bar.widget, False, False)
    
    provider.register_service(vbox, interfaces.IWidget)
    
    return provider


def create_editor(filename, action_group):
    provider = core.ServiceProvider()
    register_services(provider)
    ag = provider.get_service(interfaces.IActionGroupController)
    ag.set_action_group(action_group)
    view = provider.get_service("view")
    if filename is not None:
        file_ops = provider.get_service(interfaces.IFileOperations)
        file_ops.set_filename(filename)
        file_ops.load()
        #view.set_buffer(buff)
    
    return provider



def main():
    import sys, gobject
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = __file__
    ag = create_dummy_action_group()
    
    win = gtk.Window()
    provider = create_widget(filename, ag)
    editor = provider.get_service(interfaces.IWidget)
    editor.show()
    win.add(editor)
    win.show()
    ag.get_action(ACTION_FIND_TOGGLE).set_active(True)
    ag.get_action(ACTION_REPLACE_TOGGLE).set_active(True)

    win.connect("delete-event", gtk.main_quit)
    gtk.main()
    win.destroy()

if __name__ == '__main__':
    main()
