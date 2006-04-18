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
import common
import core

class MyServiceProvider(core.ServiceProvider):
    def __del__(self):
        self.get_service(interfaces.IWidget).destroy()

def buffer_factory(provider):
    return provider.get_service("view").get_buffer()

def register_services(service_provider):
    services = ("view", interfaces.ICarretController,
                interfaces.ISelectColors, interfaces.ISelectFont)
                
    service_provider.register_simple_factory(
        lambda service_provider: CulebraView(),
        *services
    )
    service_provider.register_simple_factory(
        widget_factory,
        interfaces.IWidget,
    )
    service_provider.register_factory(
        ActionGroupController,
        interfaces.IActionGroupController
    )
    
    service_provider.register_simple_factory(buffer_factory, "buffer")
    
    # Register other modules
    searchbar.register_services(service_provider)
    replacebar.register_services(service_provider)
    buffers.register_services(service_provider)
    
def register(registry):
    services = ("view", interfaces.ICarretController,
                interfaces.ISelectColors, interfaces.ISelectFont)
                
    service_provider.register_plugin(
        lambda service_provider: CulebraView(),
        singletons=services,
    )
    service_provider.register_plugin(
        widget_factory,
        singletons=[interfaces.IWidget],
    )
    service_provider.register_plugin(
        factory=ActionGroupController.factory(),
        singletons=[interfaces.IActionGroupController]
    )
    
    registry.register(factory=buffer_factory, singletons=["buffer"])
    
    # Register other modules
    searchbar.register(registry)
    replacebar.register(registry)
    buffers.register(registry)
    

class ActionGroupController(core.BaseService):
    search = core.Depends(interfaces.ISearchBar)
    replace = core.Depends(interfaces.IReplaceBar)
    
    def set_action_group(self, action_group):
        self.search.set_action_group(action_group)
        self.replace.set_action_group(action_group)

class CulebraView(BaseView):
    
    def __init__(self):
        super(CulebraView, self).__init__()
        super(CulebraView, self).set_buffer(BaseBuffer())
    
    
    def set_background_color(self, color):
        self.modify_base(gtk.STATE_NORMAL, color)
    
    def set_font_color(self, color):
        self.modify_text(gtk.STATE_NORMAL, color)

    def set_font(self, fontstring):
        font_desc = pango.FontDescription(fontstring)
        if font_desc is not None:
            self.modify_font(font_desc)

    def set_buffer(self, buff):
        raise AttributeError("You are not allowed to change buffers")
    
    def _on_key_pressed(self, search_text, event):
        if event.keyval == common.KEY_ESCAPE:
            self.toggle_action.set_active(False)

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

def widget_factory(provider):
    vbox = gtk.VBox(spacing=12)

    scroller = gtk.ScrolledWindow()
    scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scroller.show()
    vbox.add(scroller)
    
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
    
    return vbox
    
def create_editor(filename=None, action_group=None, encoding="utf-8"):
    provider = MyServiceProvider()
    register_services(provider)
    ag = provider.get_service(interfaces.IActionGroupController)
    ag.set_action_group(action_group)

    if filename is not None:
        file_ops = provider.get_service(interfaces.IFileOperations)
        file_ops.set_filename(filename)
        file_ops.set_encoding(encoding)
        file_ops.load()
        #view.set_buffer(buff)
    
    return provider



def main():
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = __file__
    ag = common.create_dummy_action_group()
    
    win = gtk.Window()
    provider = create_editor(filename, ag)
    editor = provider.get_service(interfaces.IWidget)
    editor.show()
    win.add(editor)
    win.show()
    ag.get_action(common.ACTION_FIND_TOGGLE).set_active(True)
    ag.get_action(common.ACTION_REPLACE_TOGGLE).set_active(True)

    win.connect("delete-event", gtk.main_quit)
    gtk.main()
    win.destroy()

if __name__ == '__main__':
    main()
