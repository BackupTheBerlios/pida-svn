# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com

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

# system imports
import time

# gtk imports
import gtk
import pango
import gobject
import contentbook

class external_window(gtk.Window):

    def __init__(self, *args):
        super(external_window, self).__init__()
        from pkg_resources import Requirement, resource_filename
        icon_file = resource_filename(Requirement.parse('pida'),
                              'pida-icon.png')
        im = gtk.Image()
        im.set_from_file(icon_file)
        pb = im.get_pixbuf()
        self.set_icon(pb)
        self.__book = contentbook.ContentBook()
        self.__book.notebook.set_show_tabs(False)
        self.add(self.__book)
        self.connect('destroy', self.on_window__destroy)
        self.resize(600, 480)
        self.set_position(gtk.WIN_POS_CENTER)
        self.__book.connect('empty', self.cb_empty)

    def cb_empty(self, holder):
        self.destroy()

    def append_page(self, page):
        self.__book.append_page(page)
        self.set_title(page.long_title)
        self.show_all()
        page.hide_title()
        page.hide_controlbox()
        self.present()

    def on_window__destroy(self, window):
        self.hide()
        self.remove(self.__book)
        self.__book.remove_pages()
        return True

class content_view(gtk.VBox):
    __gsignals__ = {'short-title-changed': (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'long-title-changed': (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'removed' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'raised' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}
    
    ICON_NAME = None

    SHORT_TITLE = None
    LONG_TITLE = None

    HAS_CONTROL_BOX = True
    HAS_CLOSE_BUTTON = True
    HAS_DETACH_BUTTON = True

    HAS_TITLE = True

    WIDGET_TYPE = None

    def __init__(self, service, prefix, widget=None, icon_name=None,
                 short_title=None, **kw):
        gtk.VBox.__init__(self)
        self.__uid = time.time()
        self.__service = service
        self.__prefix = prefix
        self.__init_actions()
        self.__init_icon(icon_name)
        self.__init_short_title(short_title)
        self.__init_long_title()
        self.__init_widgets(widget)
        self.__holder = None
        self.set_size_request(0,0)
        self.init(**kw)

    def __init_icon(self, icon_name):
        if icon_name is not None:
            self.icon_name = icon_name
        elif self.ICON_NAME is not None:
            self.icon_name = self.ICON_NAME
        else:
            self.icon_name = 'terminal'

    def __init_short_title(self, short_title):
        if short_title:
            self.short_title = short_title
        elif self.SHORT_TITLE:
            self.short_title = self.SHORT_TITLE
        else:
            self.short_title = 'Untitled'

    def __init_long_title(self):
        if self.LONG_TITLE is not None:
            self.long_title = self.LONG_TITLE
        else:
            self.long_title = 'Long title'

    def __init_widgets(self, widget):
        topbar = gtk.VBox()
        topbar.show()
        self.pack_start(topbar, expand=False)
        
        titlebar = gtk.HBox()
        titlebar.show()
        self.pack_start(titlebar, expand=False)
        
        if widget is not None:
            self.pack_start(widget)
            self.__widget = widget
        elif self.WIDGET_TYPE is not None:
            self.__widget = self.WIDGET_TYPE
            self.pack_start(self.__widget)
        else:
            self.__widget = gtk.VBox()
            self.pack_start(self.__widget)
        
        self.__widget.show()
        self.__init_topbar(topbar)
        
    def __init_topbar(self, topbar):
        self.__toolbar_area = gtk.HBox()
        self.__toolbar_area.show()
        
        topbar.pack_start(self.__toolbar_area, expand=False)
        self.__long_title_label = gtk.Label(self.__long_title)
        self.__long_title_label.show()

        self.__toolbar = gtk.Toolbar()
        self.__toolbar_area.pack_start(self.__toolbar)
        self.__toolbar.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        def _rc(tb, event):
            if event.button == 3:
                self.create_detach_popup(event)
        self.__toolbar.connect('button-press-event', _rc)
        
        if self.HAS_TITLE:
            lti = gtk.ToolItem()
            lti.set_expand(True)
            lti.add(self.__long_title_label)
            self.__toolbar.add(lti)
            #self.__toolbar_area.pack_start(self.__long_title_label, padding=6)
            self.__long_title_label.set_alignment(0.0, 0.5)
            self.__long_title_label.set_selectable(True)
            self.__long_title_label.set_ellipsize(pango.ELLIPSIZE_START)
        if self.HAS_CONTROL_BOX:
            tb = self.__toolbar
            tb.set_icon_size(gtk.ICON_SIZE_MENU)
            detbut = self.__det_act.create_tool_item()
            tb.add(detbut)
            closebut = self.__close_act.create_tool_item()
            tb.add(closebut)
            self.__close_button = closebut
            if not self.HAS_CLOSE_BUTTON:
                closebut.hide()
            if not self.HAS_DETACH_BUTTON:
                detbut.hide()

    def __init_actions(self):
        self.__det_act = gtk.ToggleAction(name='detach',
                                      label='Detach',
                                      tooltip='Detach this view',
                                      stock_id='gtk-up')
        self.__close_act = gtk.Action(name='close',
                                    label='Close',
                                    tooltip='Close this view',
                                    stock_id=gtk.STOCK_CLOSE)
        self.__close_act.connect('activate', self.cb_close_action_activated)
        self.__det_act.connect('activate', self.cb_detach_action_activated)

    def init(self):
        pass

    def close(self):
        self.remove()

    def remove(self):
        if self.__holder is not None:
            self.__holder.remove_page(self)
    
    def detach(self):
        if self.__holder is not None:
            self.__holder.detach_page(self)
            self.__holder = None

    def externalise(self):
        self.detach()
        book = external_window()
        book.append_page(self)
        if self.view_definition.book_name == 'ext':
            self.__det_act.set_sensitive(False)

    def internalise(self):
        self.detach()
        self.__det_act.set_sensitive(True)
        self.service.boss.call_command('window', 'append_page',
                view=self, bookname=self.view_definition.book_name)
        self.show_controlbox()

    def raise_page(self):
        if self.__holder is not None:
            self.__holder.set_page(self)

    def hide_title(self):
        self.__long_title_label.hide()

    def hide_controlbox(self):
        if self.HAS_CONTROL_BOX:
            self.__close_button.hide()

    def show_controlbox(self):
        if self.HAS_CONTROL_BOX:
            self.__close_button.show()

    def cb_close_action_activated(self, action):
        self.service.close_view(self)

    def cb_detach_action_activated(self, action):
        self.service.detach_view(self, action.get_active())

    def get_service(self):
        return self.__service
    
    service = property(get_service)
    
    def get_unique_id(self):
        return self.__uid
    
    unique_id = property(get_unique_id)

    def get_short_title(self):
        return self.__short_title

    def set_short_title(self, value):
        self.__short_title = value
        self.emit('short-title-changed')
 
    short_title = property(get_short_title, set_short_title)

    def get_long_title(self):
        return self.__long_title

    def set_long_title(self, value):
        self.__long_title = value
        try:
            self.__long_title_label.set_label(value)
        except AttributeError:
            pass
        self.emit('long-title-changed')
 
    long_title = property(get_long_title, set_long_title)

    def get_icon_name(self):
        return self.__icon_name
    
    def set_icon_name(self, value):
        self.__icon_name = value
    icon_name = property(get_icon_name, set_icon_name)
    
    def get_icon(self):
        return self.create_icon()
    icon = property(get_icon)

    def get_holder(self):
        return self.__holder
    
    def set_holder(self, value):
        self.__holder = value
    holder = property(get_holder, set_holder)

    def get_widget(self):
        return self.__widget
    widget = property(get_widget)

    def get_prefix(self):
        return self.__prefix
    prefix = property(get_prefix)

    def create_icon(self):
        import icons
        icon = icons.icons.get_image(self.icon_name)
        eb = self.create_tooltip_box()
        eb.add(icon)
        return eb

    def create_tooltip_box(self):
        eb = gtk.EventBox()
        eb.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        def _click(_eb, event):
            if event.button == 3:
                self.create_detach_popup(event)
                return True
        eb.connect('button-press-event', _click)
        return eb

    def create_detach_popup(self, event):
        if self.HAS_CONTROL_BOX and (self.HAS_CLOSE_BUTTON or
                                    self.HAS_DETACH_BUTTON):
            menu = gtk.Menu()
            if self.HAS_DETACH_BUTTON:
                mi = self.__det_act.create_menu_item()
                menu.add(mi)
            if self.HAS_CLOSE_BUTTON:
                mi = self.__close_act.create_menu_item()
                menu.add(mi)
            menu.show_all()
            menu.popup(None, None, None, event.button, event.time)
        

gobject.type_register(content_view)
