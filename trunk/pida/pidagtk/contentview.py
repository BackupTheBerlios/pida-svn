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
import icons


def create_pida_icon():
    from pkg_resources import Requirement, resource_filename
    icon_file = resource_filename(Requirement.parse('pida'),
                              'pida-icon.png')
    im = gtk.Image()
    im.set_from_file(icon_file)
    return im.get_pixbuf()


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
        self.__close_act.connect_after('activate', self.cb_close_action_activated)
        self.__det_act.connect_after('activate', self.cb_detach_action_activated)

    def init(self):
        pass

    def show(self):
        self.service.show_view(view=self)

    def remove(self):
        self.service.close_view(self)

    close = remove
    
    def detach(self):
        self.service.detach_view(self, self.__det_act.get_active())

    def raise_page(self):
        self.service.raise_view(self)

    def hide_title(self):
        self.__long_title_label.hide()

    def hide_controlbox(self):
        if self.HAS_CLOSE_BUTTON and self.HAS_CONTROL_BOX:
            self.__close_button.hide()

    def show_controlbox(self):
        if self.HAS_CLOSE_BUTTON and self.HAS_CONTROL_BOX:
            self.__close_button.show()

    def cb_close_action_activated(self, action):
        self.service.close_view(self)

    def cb_detach_action_activated(self, action):
        self.detach()

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
        return icons.icons.get_image(self.icon_name)

    def get_tooltip_text(self):
        tooltiptext = self.long_title
        if not tooltiptext:
            tooltiptext = self.short_title
        if not tooltiptext:
            tooltiptext = 'No tooltip set for %s' % contentview
        return tooltiptext

    def create_tooltip_box(self):
        eb = gtk.EventBox()
        eb.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        icons.tips.set_tip(eb, self.get_tooltip_text())
        def _click(_eb, event):
            if event.button == 3:
                self.create_detach_popup(event)
                return True
        eb.connect('button-press-event', _click)
        return eb

    def create_tab_label(self, vertical=False):
        label = gtk.Label(self.short_title)
        if vertical:
            box = gtk.VBox(spacing=4)
            label.set_angle(270)
        else:
            box = gtk.HBox(spacing=4)
        box.pack_start(self.icon)
        box.pack_start(label)
        eb = self.create_tooltip_box()
        eb.add(box)
        eb.show_all()
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
        

class ContentBook(gtk.Notebook):

    __gsignals__ = {'empty' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

    def __init__(self):
        super(ContentBook, self).__init__()
        self._views = {}
        self.set_scrollable(True)
        self.set_show_border(False)
        self.set_property('tab-border', 2)
        self.set_property('homogeneous', False)
        self.set_tab_pos(gtk.POS_TOP)
        self.popup_disable()

    def raise_view(self, view):
        self.set_current_page(self.page_num(view))

    def raise_uid(self, uid):
        self.raise_view(self._views[uid])

    def add(self, view, raise_page=True):
        vertical = self.get_tab_pos() in [gtk.POS_LEFT, gtk.POS_RIGHT]
        tab_label=view.create_tab_label(vertical)
        self.append_page(view, tab_label)
        view.show_controlbox()
        view.show_all()
        self._views[view.unique_id] = view
        if raise_page:
            self.raise_view(view)

    def remove_view(self, view):
        self.remove_page(self.page_num(view))
        del self._views[view.unique_id]
        if len(self._views) == 0:
            self.emit('empty')

    def remove_uid(self, uid):
        self.remove_view(self._views[uid])

    def has_uid(self, uid):
        return (uid in self._views)

    def next_page(self):
        if self.get_current_page() == self.get_n_pages() - 1:
            self.set_current_page(0)
        else:
            gtk.Notebook.next_page(self)

    def prev_page(self):
        if self.get_current_page() == 0:
            self.set_current_page(-1)
        else:
            gtk.Notebook.prev_page(self)


class ExternalBook(object):

    def __init__(self):
        self._views = {}
        self._windows = {}

    def add(self, view):
        view.hide_controlbox()
        self._views[view.unique_id] = view
        w = gtk.Window()
        w.add(view)
        def _t(v):
            w.set_title(view.long_title)
        _t(None)
        view.connect('long-title-changed', _t)
        self._windows[view.unique_id] = w
        w.connect('delete-event', self.cb_delete, view)
        w.set_position(gtk.WIN_POS_CENTER)
        w.resize(600, 480)
        w.set_icon(create_pida_icon())
        w.show_all()
        view.hide_title()

    def remove_view(self, view):
        win = self._windows[view.unique_id]
        win.remove(view)
        del self._views[view.unique_id]
        del self._windows[view.unique_id]
        win.destroy()

    def remove_uid(self, uid):
        self.remove_view(self._views[uid])
        
    def cb_delete(self, win, event, view):
        self.remove_view(view)

    def has_uid(self, uid):
        return uid in self._views

class ContentManager(object):
    
    def __init__(self):
        self._books = {'ext': ExternalBook()}

    def create_book(self, bookname):
        book = ContentBook()
        self._books[bookname] = book
        return book

    def add(self, bookname, view):
        self._books[bookname].add(view)
    
    def raise_uid(self, uid):
        for book in self._books.values():
            if book.has_uid(uid):
                book.raise_uid(uid)
                return
        raise KeyError('view not found')

    def raise_view(self, view):
        self.raise_uid(view.unique_id)

    def remove(self, view):
        self.remove_uid(view.unique_id)

    def remove_uid(self, uid):
        for book in self._books.values():
            if book.has_uid(uid):
                book.remove_uid(uid)
                return
        raise KeyError('view not found')

gobject.type_register(ContentBook)
gobject.type_register(content_view)
