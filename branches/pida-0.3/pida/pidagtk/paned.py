import gtk
import gobject


class sizer(gtk.EventBox):
    __gsignals__ = {'dragged' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_INT, gobject.TYPE_INT)),
                    'clicked' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'drag-started' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'drag-stopped' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

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
            cursor = gtk.gdk.Cursor(gtk.gdk.SB_H_DOUBLE_ARROW)
            self.window.set_cursor(cursor)
            return True
        self.connect('map-event', mapped)
        self.set_size_request(-1, 6)

    def cb_release(self, eb, ev):
        self.drag_unhighlight()
        #self.grab_remove()
        self.emit('drag-stopped')
        self.emit('clicked')
        return True

    def cb_press(self, eb, ev):
        self.__x, self.__y = self.get_pointer()
        self.drag_highlight()
        #self.grab_add()
        self.emit('drag-started')
        return True

    def cb_motion(self, eb, ev):
        x, y = self.get_pointer()
        diffx = x - self.__x
        diffy = y - self.__y
        self.emit('dragged', diffx, diffy)

gobject.type_register(sizer)
    

class paned(gtk.EventBox):
    
    __gsignals__ = {'dragged-to' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_INT, ))}

    handle_width = 12

    def __init__(self, pos, win):
        gtk.EventBox.__init__(self)
        self.__window = win
        self.__main_widget = None
        self.__pane_widget = None
        self.__pane_holder = gtk.VBox()
        self.__pane_hidden=gtk.VBox()
        self.__pane_floater = gtk.Window()
        self.__pane_floater.set_transient_for(win)
        #self.__pane_floater.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.__pane_floater.connect('focus-out-event',
                                    self.cb_floater_lost_focus)
        self.__pane_floater.connect('event',
                                    self.cb_floater_event)
        self.__pane_floater.set_decorated(False)
        self.__pane_holder.set_no_show_all(True)
        self.__bar = sizer()
        if pos in [gtk.POS_LEFT, gtk.POS_RIGHT]:
            self.__bar_holder = gtk.VBox()
            self.__bar_holder.set_size_request(self.handle_width, -1)
            box = gtk.HBox()
        else:
            self.__bar_holder = gtk.HBox()
            self.__bar_holder.set_size_request(-1, self.handle_width)
            box = gtk.VBox()
        self.add(box)
        self.__stick_button = gtk.ToggleButton()
        self.__bar_holder.pack_start(self.__stick_button,expand=False)
        self.__drag_button = sizer()
        self.__bar_holder.pack_start(self.__drag_button, expand=False)
        self.__drag_button.set_size_request(12, 12)
        self.__drag_button.connect('dragged', self.cb_dragbutton_dragged)
        self.__drag_button.connect('drag-started', self.cb_dragbutton_started)
        self.__drag_button.connect('drag-stopped', self.cb_dragbutton_stopped)
        self.__stick_button.connect('toggled', self.cb_stick_but_toggled)
        self.__bar_holder.pack_start(self.__bar)
        self.__bar_holder.set_sensitive(False)
        self.__bar_holder.set_no_show_all(True)
        self.__bar_holder.hide_all()
        self.__bar.connect('dragged', self.cb_bar_dragged)
        self.__bar.connect('clicked', self.cb_bar_clicked)
        self.__main_holder = gtk.VBox()
        if pos in [gtk.POS_LEFT, gtk.POS_TOP]:
            box.pack_start(self.__pane_holder, expand=False)
            box.pack_start(self.__bar_holder, expand=False)
            box.pack_start(self.__main_holder)
        else:
            box.pack_start(self.__main_holder)
            box.pack_start(self.__bar_holder, expand=False)
            box.pack_start(self.__pane_holder, expand=False)
        self.__pos = pos
        self.__open = False
        self.__sticky = False
        self.__pane_width = 150

    def set_main_widget(self, main_widget):
        self.main_widget = main_widget
        self.__main_holder.pack_start(main_widget)

    def set_pane_widget(self, pane_widget):
        self.__pane_widget = pane_widget
        self.__pane_holder.add(pane_widget)
        self.__bar_holder.set_sensitive(True)
        self.__bar_holder.set_no_show_all(False)
        self.__bar_holder.show_all()
        self.show_all()
        print 'h', self.__pos
        self.hide_pane()

    def unset_pane_widget(self):
        self.hide_pane()
        self.__pane_hidden.remove(self.__pane_widget)
        self.__pane_widget = None
        self.__bar_holder.set_sensitive(False)
        self.__bar_holder.hide_all()
        self.__bar_holder.set_no_show_all(True)

    def show_pane(self):
        self.__pane_widget.reparent(self.__pane_holder)
        self.update_size()
        self.__pane_holder.show()
        self.__pane_widget.show_all()
        self.__open = True

    def set_sticky(self, stickiness):
        self.hide_pane()
        self.__sticky = stickiness
        if stickiness:
            print stickiness
            self.show_pane()
        else:
            self.hide_pane()

    def hide_pane(self):
        if not self.__sticky:
            self.__pane_widget.reparent(self.__pane_hidden)
            self.__open = False
            self.__pane_holder.hide()
            self.__pane_floater.hide()

    def float_pane(self):
        self.__pane_widget.reparent(self.__pane_floater)
        self.update_size()
        self.__pane_floater.show_all()
        self.__pane_floater.grab_focus()
        self.__open = True

    def update_size(self):
        print self.__pane_width
        alloc = self.get_allocation()
        walloc = self.__window.get_allocation()
        wx, wy = self.__window.window.get_position()
        x, y, w, h, col = self.__window.window.get_geometry()
        if self.__pos == gtk.POS_LEFT:
            self.__pane_floater.move(wx, wy)
            self.__pane_floater.resize(self.__pane_width, h)
            self.__pane_holder.set_size_request(self.__pane_width, -1)
        elif self.__pos == gtk.POS_TOP:
            self.__pane_floater.move(wx, wy)
            self.__pane_floater.resize(w, self.__pane_width)
            self.__pane_holder.set_size_request(-1, self.__pane_width)
        elif self.__pos == gtk.POS_RIGHT:
            px = wx + w - self.__pane_width - self.handle_width
            self.__pane_floater.move(px, wy)
            self.__pane_floater.resize(self.__pane_width, h)
            self.__pane_holder.set_size_request(self.__pane_width, -1)
        elif self.__pos== gtk.POS_BOTTOM:
            self.__pane_floater.move(wx, wy + h - self.__pane_width)
            self.__pane_floater.resize(w, self.__pane_width)
            self.__pane_holder.set_size_request(-1, self.__pane_width)
        self.__window.size_allocate(walloc)
        #self.__pane_holder.set_size_request(self.__pane_width, -1)

    def is_open(self):
        return self.__open

    def get_pane_widget(self):
        return self.__pane_widget

    def cb_floater_lost_focus(self, win, event):
        self.hide_pane()

    def cb_dragbutton_started(self, sizer):
        dwindow = pane_dropper(self.__window)
        winx, winy = self.__window.get_position()
        relpx, relpy = self.get_pointer()
        pointerx = relpx + winx
        pointery = relpy + winy
        dwindow.popup(pointerx, pointery)
        self.__dwindow = dwindow
        self.__targx = 0
        self.__targy = 0

    def cb_dragbutton_stopped(self, sizer):
        self.__dwindow.hide_all()
        self.emit('dragged-to', self.__targ)

    def cb_dragbutton_dragged(self, sizer, xdiff, ydiff):
        self.__targx = xdiff - self.__targx
        self.__targy = ydiff - self.__targy
        if abs(self.__targx) > abs(self.__targy):
            if self.__targx > 0:
                targ = gtk.POS_RIGHT
            else:
                targ = gtk.POS_LEFT
        else:
            if self.__targy < 0:
                targ = gtk.POS_TOP
            else:
                targ = gtk.POS_BOTTOM
        self.__dwindow.set_selected(targ)
        self.__targ = targ


    def cb_bar_dragged(self, sizer, diffx, diffy):
        if self.__sticky:
            if self.__pos in [gtk.POS_LEFT, gtk.POS_RIGHT]:
                diff = diffx
            else:
                diff = diffy
            if self.__pos in [gtk.POS_RIGHT, gtk.POS_BOTTOM]:
                diff = diff * -1
            self.__pane_width = self.__pane_width + diff
            self.update_size()
        else:
            self.cb_bar_clicked(sizer)

    def cb_bar_clicked(self, sizer):
        if not self.__sticky:
            self.float_pane()

    def cb_floater_event(self, window, event):
        self.__pane_floater.chain(event)

    def cb_stick_but_toggled(self, button):
        self.set_sticky(button.get_active())

class pane_dropper(gtk.Window):

    def __init__(self, win):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.__window = win
        self.__targets = {}
        vbox = gtk.VBox()
        self.add(vbox)
        for pos in [gtk.POS_TOP, gtk.POS_LEFT, gtk.POS_BOTTOM, gtk.POS_RIGHT]:
            a = gtk.EventBox()
            l = gtk.Label(pos.value_nick)
            a.add(l)
            a.connect('enter-notify-event', self.cb_motion,pos)
            self.__targets[pos] = a
            vbox.pack_start(a)
        self.show_all()

    def popup(self, x, y):
        self.move(x, y)
        self.show_all()

    def set_selected(self, selpos):
        for pos, widget in self.__targets.iteritems():
            if pos is selpos:
                widget.drag_highlight()
            else:
                widget.drag_unhighlight()
            
        

    def cb_motion(self, arrow, pos):
        print dir(pos)

    def cb_event(self, widget, event):
        print event.type
        self.chain(event)


class paned_window(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.__paneds = {}
        hbox = gtk.HBox()
        self.add(hbox)
        self.__paneds[gtk.POS_LEFT] = paned(gtk.POS_LEFT, self)
        hbox.pack_start(self.__paneds[gtk.POS_LEFT], expand=False)
        vbox = gtk.VBox()
        hbox.pack_start(vbox)
        self.__paneds[gtk.POS_RIGHT] = paned(gtk.POS_RIGHT, self)
        hbox.pack_start(self.__paneds[gtk.POS_RIGHT], expand=False)
        self.__paneds[gtk.POS_TOP] = paned(gtk.POS_TOP, self)
        vbox.pack_start(self.__paneds[gtk.POS_TOP], expand=False)
        self.__main_widget = gtk.EventBox()
        vbox.pack_start(self.__main_widget)
        self.__paneds[gtk.POS_BOTTOM] = paned(gtk.POS_BOTTOM, self)
        vbox.pack_start(self.__paneds[gtk.POS_BOTTOM], expand=False)
        for pos, pane in self.__paneds.iteritems():
            pane.connect('dragged-to', self.cb_dragged_to, pos)

    def set_main_widget(self, widget):
        self.__main_widget.add(widget)

    def set_pane_widget(self, pos, widget):
        self.__paneds[pos].set_pane_widget(widget)

    def cb_dragged_to(self, pane, to_pos, from_pos):
        if from_pos != to_pos:
            pane_widget = pane.get_pane_widget()
            pane.unset_pane_widget()
            self.set_pane_widget(to_pos, pane_widget)

if __name__ == '__main__':
    window = paned_window()
    window.set_default_size(400, 300)
    window.connect("destroy", gtk.main_quit)

    #paned = Paned(gtk.POS_BOTTOM, window)
    #hbox.pack_start(paned, True, True, 0)
    textview = gtk.TextView()
    window.set_main_widget(textview)
    textview.show()


    for pos in [gtk.POS_LEFT, gtk.POS_BOTTOM]:
        label = gtk.Entry()
        window.set_pane_widget(pos, label)

    window.show_all()
    gtk.main()
