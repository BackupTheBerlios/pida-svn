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
        self.set_size_request(50, -1)
        self.__icon = None
        if icon is not None:
            self.__icon = icon
            self.__b.pack_start(self.__icon, expand=False, padding=4)
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
        self.set_size_request(-1, 6)

    def cb_release(self, eb, ev):
        if self.__dragging:
            self.__dragging = False
            diff = ev.y - self.__dragy
            self.emit('dragged', diff)
        self.drag_unhighlight()
        return True

    def cb_press(self, eb, ev):
        self.__dragging = True
        self.__dragy = ev.y
        self.drag_highlight()
        return True


class clickable_eventbox(gtk.EventBox):

    gsignal('clicked')

    def __init__(self, widget=None):
        gtk.EventBox.__init__(self)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.connect('button-press-event', self.cb_pressed)
        self.connect('button-release-event', self.cb_released)
        if widget is not None:
            self.add(widget)

    def cb_pressed(self, eventbox, event):
        pass

    def cb_released(self, eventbox, event):
        if event.button == 1:
            self.emit('clicked')
        

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
