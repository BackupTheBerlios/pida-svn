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

# gtk import(s)
import gtk
import gobject
import icons

from pida.utils.kiwiutils import gproperty, gsignal

class question_box(gtk.HBox):

    def __init__(self):
        gtk.HBox.__init__(self)
        self.__entry = gtk.Entry()
        self.pack_start(self.__entry)
        self.__toolbar = toolbar.Toolbar()
        self.pack_start(self.__toolbar)
        self.__toolbar.add_button('ok', 'apply', 'ok')
        self.__toolbar.add_button('cancel', 'cancel', 'cancel')
        self.__toolbar.connect('clicked', self.cb_toolbar_clicked)
        self.set_sensitive(False)

    def cb_toolbar_clicked(self, toolbar, action):
        if action == 'ok':
            self.__current_callback(self.__entry.get_text())
        self.__entry.set_text('')
        self.set_sensitive(False)

    def question(self, callback, prompt='?'):
        self.set_sensitive(True)
        self.__current_callback = callback


class hyperlink(gtk.EventBox):
    __gsignals__ = {'clicked' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

    def __init__(self, label, icon=None):
        gtk.EventBox.__init__(self)
        self.__b = gtk.HBox()
        self.add(self.__b)
        self.__mode = 'normal'
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.ENTER_NOTIFY_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK)
        self.connect('enter-notify-event', self.cb_mouse_entered)
        self.connect('leave-notify-event', self.cb_mouse_left)
        self.connect('button-press-event', self.cb_mouse_pressed)
        self.connect('button-release-event', self.cb_mouse_released)
        self.__label = gtk.Label()
        self.__label.set_property('justify', gtk.JUSTIFY_CENTER)
        #self.set_size_request(50, -1)
        self.__icon = None
        if icon is not None:
            self.__icon = icon
            self.__b.pack_start(self.__icon, expand=False, padding=0)
        self.__b.pack_start(self.__label, expand=False, fill=True, padding=4)
        self.__text = label
        self.set_normal()

    def cb_mouse_entered(self, *a):
        self.set_highlighted()

    def cb_mouse_left(self, *a):
        self.set_normal()

    def cb_mouse_pressed(self, *a):
        self.set_activated()
        return True

    def cb_mouse_released(self, *a):
        self.set_highlighted()
        self.emit('clicked')
        return True

    def set_highlighted(self):
        self.__label.set_markup(HIGH_MU % self.markup_text)

    def set_activated(self):
        self.__label.set_markup(ACT_MU % self.markup_text)

    def set_selected(self):
        self.__mode = 'selected'
        self.set_normal()

    def set_unselected(self):
        self.__mode = 'normal'
        self.set_normal()

    def set_normal(self):
        self.__label.set_markup(NORMAL_MU % self.markup_text)
        self.set_icon_sensitivity()
    
    def set_icon_sensitivity(self):
        if self.__icon is None:
            return
        if self.__mode == 'selected':
            self.__icon.set_sensitive(True)
        else:
            self.__icon.set_sensitive(False)

    def set_text(self, text):
        self.__text = text
        self.set_normal()

    def get_markup_text(self):
        S = '%s'
        if self.__mode == 'selected':
            S = '<u>%s</u>'
        return S % self.__text
    markup_text = property(get_markup_text)


class sizer(gtk.EventBox):
    __gsignals__ = {'dragged' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_INT, ))}

    def __init__(self):
        gtk.EventBox.__init__(self)
        self.__vb = gtk.HBox()
        self.__b = gtk.Frame()
        self.add(self.__b)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK)
        uparrow = gtk.Arrow(gtk.ARROW_UP, gtk.SHADOW_ETCHED_IN)
        self.__vb.pack_start(uparrow, expand=False)
        downarrow = gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_ETCHED_IN)
        self.__vb.pack_start(downarrow, expand=False)
        self.connect('button-press-event', self.cb_press)
        self.connect('button-release-event', self.cb_release)
        self.connect('motion-notify-event', self.cb_motion)
        def mapped(slf, eb, *args):
            cursor = gtk.gdk.Cursor(gtk.gdk.DOUBLE_ARROW)
            self.window.set_cursor(cursor)
        self.connect('map-event', mapped)
        self.set_size_request(-1, 6)

    def cb_release(self, eb, ev):
        self.drag_unhighlight()
        self.emit('dragged', self.__y - ev.y)
        return True

    def cb_press(self, eb, ev):
        self.__dragging = True
        self.__y = ev.y
        self.drag_highlight()
        return True

    def cb_motion(self, eb, event):
        print event.x, event.y
        pass


class clickable_eventbox(gtk.EventBox):

    gsignal('clicked')
    gsignal('popup')
    gsignal('active')
    gsignal('unactive')

    def __init__(self, widget=None, menu=None):
        gtk.EventBox.__init__(self)
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

    def popup(self, event, menu=None):
        """Popup the menu."""
        if menu is None:
            menu = self.__menu
        if menu is not None:
            menu.popup(None, None, None, event.button, event.time)
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

    def on_button_press_event(self, eventbox, event):
        if event.button == 1:
            self.grab_add()
            self.__clickedstate = True
            self.emit('active')
        elif event.button == 3:
            self.popup(event)

    def on_button_release_event(self, eventbox, event):
        if event.button == 1:
            self.grab_remove()
            if self.__clickedstate:
                self.clicked()
                self.__clickedstate = False
                self.emit('unactive')

gobject.type_register(clickable_eventbox)

import gobject
from cgi import escape

class hyper_link(clickable_eventbox):

    gproperty('normal-markup', str,
              '<span color="#0000c0">%s</span>')
    gproperty('active-markup', str,
              '<span color="#c00000">%s</span>')
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


gobject.type_register(hyper_link)


def demo():
    w = gtk.Window()
    w.connect('destroy', lambda win: gtk.main_quit())
    h1 = gtk.HBox()
    v1 = gtk.VBox()
    w.add(v1)
    e = gtk.Label('nothing clicked yet')
    def clicked(hyperlink, i):
        e.set_label('hyperlink-%s' % i)
    def popup(hyperlink, i):
        e.set_label('link popup %s' % i)
    links = ['Hyperlinks!', 'for', 'pygtk', 'I have a popup menu',
             'me too right click me!']
    for i in range(5):
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
    





        

class control_box(gtk.HBox):

    gsignal('detach-clicked')
    gsignal('close-clicked')

    icon_theme = gtk.IconTheme()
    icon_theme.set_custom_theme('Humility')
    load_flags = gtk.ICON_LOOKUP_FORCE_SVG
    
    close_pixbuf = icon_theme.load_icon('gtk-close', 14, load_flags)
    detach_pixbuf = icon_theme.load_icon('gtk-go-up', 12, load_flags)

    def __init__(self, detach_button=True, close_button=True):
        gtk.HBox.__init__(self)
        db = clickable_eventbox(self.get_detach_image())
        db.connect('clicked', self.cb_detach_clicked)
        if detach_button:
            self.pack_start(db)
        cb = clickable_eventbox(self.get_close_image())
        cb.connect('clicked', self.cb_close_clicked)
        if close_button:
            self.pack_start(cb)

    def cb_close_clicked(self, eventbox):
        self.emit('close-clicked')

    def cb_detach_clicked(self, eventbox):
        self.emit('detach-clicked')

    def get_close_image(self):
        close_image = gtk.Image()
        close_image.set_from_pixbuf(self.close_pixbuf)
        return close_image
    
    def get_detach_image(self):
        detach_image = gtk.Image()
        detach_image.set_from_pixbuf(self.detach_pixbuf)
        return detach_image


HL_MU = """<span color="%s">%%s</span>"""
NORMAL_MU = HL_MU % '#0000c0'
HIGH_MU = HL_MU % '#c00000'
ACT_MU = HL_MU % '#000000'
