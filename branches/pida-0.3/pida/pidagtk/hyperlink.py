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

import gtk
from cgi import escape

from kiwi.utils import gsignal, gproperty

class clickable_eventbox(gtk.EventBox):

    gsignal('clicked')
    gsignal('popup')
    gsignal('active')
    gsignal('unactive')

    def __init__(self, widget=None, menu=None):
        gtk.EventBox.__init__(self)
        self.connect('map-event', self.on_map_event)
        # initialise the event box
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.connect('button-press-event', self.on_button_press_event)
        self.connect('button-release-event', self.on_button_release_event)
        self.__widget = widget
        if widget is not None:
            self.add(widget)
        self.__menu = menu
        self.__clickedstate = False

    # public API

    def popup(self, menu=None, button=3, etime=0):
        """Popup the menu and emit the popup signal.

        @var event: the gtk.gdk event that fired the popup. Note: this can be
        any object with the time and button paramters"""
        if menu is None:
            menu = self.__menu
        if menu is not None:
            menu.popup(None, None, None, button, etime)
        self.emit('popup')

    def set_menu(self, menu):
        """Set the menu."""
        self.__menu = menu

    def has_menu(self):
        """Whether the widget has a menu set."""
        return self.__menu is not None

    def clicked(self):
        self.emit('clicked')

    def get_widget(self):
        return self.__widget

    # signal callbacks

    def on_button_press_event(self, eventbox, event):
        if event.button == 1:
            self.grab_add()
            self.__clickedstate = True
            self.emit('active')
        elif event.button == 3:
            self.popup(button=event.button)

    def on_button_release_event(self, eventbox, event):
        if event.button == 1:
            self.grab_remove()
            if self.__clickedstate:
                self.clicked()
                self.__clickedstate = False
                self.emit('unactive')

    def on_map_event(self, eventbox, event):
        cursor = gtk.gdk.Cursor(gtk.gdk.HAND1)
        self.window.set_cursor(cursor)

class hyper_link(clickable_eventbox):

    gproperty('normal-markup', str,
              '<span color="#0000c0">%s</span>')

    gproperty('active-markup', str,
              '<u><span color="#c00000">%s</span></u>')

    gproperty('hover-markup', str,
              '<u><span color="#0000c0">%s</span></u>')

    def __init__(self, text=''):
        self.__gproperties = {}
        self.__label = gtk.Label()
        clickable_eventbox.__init__(self, self.__label)
        self.set_border_width(1)
        self.add_events(gtk.gdk.ENTER_NOTIFY_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK)
        self.connect('enter-notify-event', self.on_hover_changed, True)
        self.connect('leave-notify-event', self.on_hover_changed, False)
        self.connect('active', self.on_active_changed, True)
        self.connect('unactive', self.on_active_changed, False)
        self.__text = None
        self.__is_active = False
        self.__is_hover = False
        self.set_text(text)

    def do_set_property(self, prop, value):
        self.__gproperties[prop.name] = value

    def do_get_property(self, prop):
        return self.__gproperties.setdefault(prop.name, prop.default_value)

    def set_text(self, text):
        self.__text = text
        self.__update_look()

    def on_hover_changed(self, eb, event, hover):
        self.__is_hover = hover
        self.__update_look()
        
    def on_active_changed(self, eb, active):
        self.__is_active = active
        self.__update_look()

    def __update_look(self):
        if self.__is_active:
            state = 'active'
        elif self.__is_hover:
            state = 'hover'
        else:
            state = 'normal'
        markup_string = self.get_property('%s-markup' % state)
        self.__label.set_markup(markup_string % escape(self.__text))



def demo():
    w = gtk.Window()
    w.connect('destroy', lambda win: gtk.main_quit())
    h1 = gtk.HBox()
    v1 = gtk.VBox()
    w.add(v1)
    e = gtk.Label('nothing clicked yet')
    def clicked(hyperlink, i):
        e.set_label('hyperlink-%s' % i)
    def popup(hyperlink, s):
        e.set_label(i)
    links = ['Hyperlinks!', 'for', 'pygtk', 'I have a popup menu',
             'me too right click me!']
    for i in range(5):
        w.show_all()
        hl = hyper_link(links[i])
        hl.connect('clicked', clicked, i)
        hl.connect('popup', clicked, i)
        v1.pack_start(hl)
        if i > 2:
            m = gtk.Menu()
            mi = gtk.MenuItem()
            mi.add(gtk.Label('menus can be'))
            m.add(mi)
            mi = gtk.MenuItem()
            mi.add(gtk.Label('set by using'))
            m.add(mi)
            mi = gtk.MenuItem()
            mi.add(gtk.Label('hyperlink.set_menu'))
            m.add(mi)
            m.show_all()
            hl.set_menu(m)
    v1.pack_start(e)
    w.show_all()
    gtk.main()
    
if __name__ == '__main__':
    demo()



