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

# pidagtk import(s)
import toolbar
import widgets
import paned

# system imports
import time

# gtk imports
import gtk
import gobject

import pida.utils.kiwiutils as kiwiutils

class content_view(gtk.VBox):
    __gsignals__ = {'short-title-changed': (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'long-title-changed': (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'action' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'removed' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'raised' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}
    
    #kutils.gproperty('icon-name', ktypes.str, default='')

    ICON_NAME = None

    SHORT_TITLE = None
    LONG_TITLE = None

    HAS_CONTROL_BOX = True
    HAS_CLOSE_BUTTON = True
    HAS_DETACH_BUTTON = True

    HAS_TITLE = True

    HAS_TOOLBAR = True

    WIDGET_TYPE = None

    BUTTONS = []

    def __init__(self, service, prefix, widget=None, icon_name=None, **kw):
        gtk.VBox.__init__(self)
        self.__uid = time.time()
        self.__service = service
        self.__prefix = prefix
        self.__init_icon(icon_name)
        self.__init_short_title()
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

    def __init_short_title(self):
        if self.SHORT_TITLE:
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
        # TODO: check if toolbar.Toolbar needs work too
        self.__toolbar = toolbar.Toolbar()
        self.__toolbar.show()
        
        self.__toolbar_area.pack_start(self.__toolbar, expand=False)
        self.__toolbar.connect('clicked', self.cb_toolbar_clicked)
        for name, icon, tooltip in self.BUTTONS:
            self.__toolbar.add_button(name, icon, tooltip)
        if self.HAS_CONTROL_BOX:
            if self.HAS_DETACH_BUTTON:
                detbut = paned.sizer('menu')
                self.__toolbar_area.pack_start(detbut, expand=False)
                detbut.connect('clicked',
                            self.cb_controlbar_detach_clicked)
        self.__long_title_label = gtk.Label(self.__long_title)
        self.__long_title_label.show()
        
        if self.HAS_TITLE:
            self.__toolbar_area.pack_start(self.__long_title_label, padding=6)
            self.__long_title_label.set_alignment(0.0, 0.5)
            self.__long_title_label.set_selectable(True)
        if self.HAS_CONTROL_BOX:
            if self.HAS_CLOSE_BUTTON:
                align = gtk.Alignment()
                align.show()
                self.__toolbar_area.pack_start(align)
                
                closebut = paned.sizer('close')
                closebut.show()
                
                self.__toolbar_area.pack_start(closebut, expand=False)
                closebut.connect('clicked',
                            self.cb_controlbar_close_clicked)

    def init(self):
        pass

    def toolbar_add_button(self, name, icon, tooltip):
        self.__toolbar.add_button(name, icon, tooltip)

    def toolbar_add_widget(self, widget, **kw):
        widget.show()
        self.__toolbar.add_widget(widget, **kw)

    def toolbar_add_separator(self):
        self.__toolbar.add_separator()

    def close(self):
        self.remove()

    def remove(self):
        if self.__holder is not None:
            self.__holder.remove_page(self)
    
    def detach(self):
        if self.__holder is not None:
            self.__holder.detach_page(self)

    def raise_page(self):
        if self.__holder is not None:
            self.__holder.set_page(self)

    def cb_toolbar_clicked(self, toolbar, name):
        func = 'cb_%s_toolbar_clicked_%s' % (self.__prefix, name)
        cb = getattr(self.service, func, None)
        if cb is not None:
            cb(self, toolbar, name)
        self.emit('action', name)

    def cb_controlbar_close_clicked(self, controlbox):
        self.__controlbar_clicked('close')

    def cb_controlbar_detach_clicked(self, controlbox):
        self.__controlbar_clicked('detach')

    def __controlbar_clicked(self, name):
        func = 'cb_%s_controlbar_clicked_%s' % (self.__prefix, name)
        cb = getattr(self.service, func, None)
        if cb is not None:
            cb(self, toolbar, name)

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
        import icons
        return icons.icons.get_image(self.icon_name)
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

gobject.type_register(content_view)
