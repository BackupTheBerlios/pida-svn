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

"""A module containing a hyper link widget."""


from cgi import escape

import gtk

from kiwi.utils import gsignal, gproperty


class HyperLink(gtk.EventBox):
    """
    A hyperlink widget.

    This widget behaves much like a hyperlink from a browser. The markup that
    will be displayed is contained in the properties normal-markup
    hover-markup and active-markup. There is a clicked signal which is fired
    when hyperlink is clicked with the left mouse button.

    Additionally, the user may set a menu that will be popped up when the user
    right clicks the hyperlink.
    """

    gproperty('normal-color', str, '#0000c0')

    gproperty('normal-underline', bool, False)

    gproperty('normal-bold', bool, False)

    gproperty('hover-color', str, '#0000c0')

    gproperty('hover-underline', bool, True)

    gproperty('hover-bold', bool, False)

    gproperty('active-color', str, '#c00000')

    gproperty('active-underline', bool, True)

    gproperty('active-bold', bool, False)

    gsignal('clicked')

    gsignal('right-clicked')

    def __init__(self, text='', menu=None):
        """
        Create a new hyperlink.

        @param text: The text of the hyperlink.
        @type text: str
        """
        gtk.EventBox.__init__(self)
        self._gproperties = {}
        self._text = text
        self._is_active = False
        self._is_hover = False
        self._menu = menu
        self._label = gtk.Label()
        self.add(self._label)
        self.set_text(text)
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.ENTER_NOTIFY_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK)
        self.connect('button-press-event', self._on_button_press_event)
        self.connect('button-release-event', self._on_button_release_event)
        self.connect('enter-notify-event', self._on_hover_changed, True)
        self.connect('leave-notify-event', self._on_hover_changed, False)
        self.connect('map-event', self._on_map_event)

    def do_set_property(self, prop, value):
        self._gproperties[prop.name] = value

    def do_get_property(self, prop):
        return self._gproperties.setdefault(prop.name, prop.default_value)

    def get_text(self):
        return self._text

    def set_text(self, text):
        """
        Set the text of the hyperlink.
        
        @param text: The text to set the hyperlink to.
        @type text: str
        """
        self._text = text
        self._update_look()

    def set_menu(self, menu):
        """
        Set the menu to be used for popups.

        @param menu: the gtk.Menu to be used.
        @type menu: gtk.Menu
        """
        self._menu = menu

    def has_menu(self):
        """
        Return whether the widget has a menu set.
        
        @return: a boolean value indicating whether the internal menu has been
            set.
        """
        return self._menu is not None

    def popup(self, menu=None, button=3, etime=0):
        """
        Popup the menu and emit the popup signal.

        @param menu: The gtk.Menu to be popped up. This menu will be
            used instead of the internally set menu. If this parameter is not
            passed or None, the internal menu will be used.
        @type menu: gtk.Menu

        @param button: An integer representing the button number pressed to
            cause the popup action.
        @type button: int

        @param time: The time that the popup event was initiated.
        @type time: long
        """
        if menu is None:
            menu = self._menu
        if menu is not None:
            menu.popup(None, None, None, button, etime)
        self.emit('right-clicked')

    def clicked(self):
        """
        Fire a clicked signal.
        """
        self.emit('clicked')

    def get_label(self):
        """
        Get the internally stored widget.
        """
        return self._label

    def _update_look(self):
        """
        Update the look of the hyperlink depending on state.
        """
        if self._is_active:
            state = 'active'
        elif self._is_hover:
            state = 'hover'
        else:
            state = 'normal'
        color =  self.get_property('%s-color' % state)
        underline =  self.get_property('%s-underline' % state)
        bold =  self.get_property('%s-bold' % state)
        markup_string = self._build_markup(self._text, color, underline, bold)
        self._label.set_markup(markup_string)

    def _build_markup(self, text, color, underline, bold):
        """
        Build a marked up string depending on parameters.
        """
        out = '<span color="%s">%s</span>' % (color, escape(text))
        if underline:
            out = '<u>%s</u>' % out
        if bold:
            out = '<b>%s</b>' % out
        return out

    # signal callbacks

    def _on_button_press_event(self, eventbox, event):
        """
        Called on mouse down.
        
        Behaves in 2 ways.
            1. if left-button, register the start of a click and grab the
                mouse.
            1. if right-button, emit a right-clicked signal +/- popup the
                menu.
        """
        if event.button == 1:
            self.grab_add()
            self._is_active = True
            self._update_look()
        elif event.button == 3:
            self.popup(button=event.button, etime=event.time)

    def _on_button_release_event(self, eventbox, event):
        """
        Called on mouse up.
    
        If the left-button is released and the widget was earlier activated by
        a mouse down event a clicked signal is fired.
        """
        if event.button == 1:
            self.grab_remove()
            if self._is_active:
                self.clicked()
                self._is_active = False
                self._update_look()

    def _on_hover_changed(self, eb, event, hover):
        """
        Called when the mouse pinter enters or leaves the widget.
        
        @param hover: Whether the mouse has entered the widget.
        @type hover: boolean
        """
        self._is_hover = hover
        self._update_look()

    def _on_map_event(self, eventbox, event):
        """
        Called on initially mapping the widget.

        Used here to set the cursor type.
        """
        cursor = gtk.gdk.Cursor(gtk.gdk.HAND1)
        self.window.set_cursor(cursor)


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
        hl = HyperLink(links[i])
        hl.connect('clicked', clicked, i)
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



