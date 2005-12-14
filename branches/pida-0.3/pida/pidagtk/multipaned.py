

#! /usr/bin/python

import gtk
import gobject
minh = 32

class multi_paned(gtk.EventBox):


    def __init__(self):
        gtk.EventBox.__init__(self)
        self.__b = gtk.VBox()
        self.add(self.__b)
        self.__panes = []
        def mapped(eb, *args):
            myh = self.get_allocation()[3]
            if myh > 1:
                for pane in self.__panes:
                    #pane.set_size_request(-1, minh)
                    pane.set_size_request(-1, myh / len(self.__panes))
            self.size_allocate(self.get_allocation())
        self.__shrunk = {}
        self.connect_after('map-event', mapped)
        
    def add_pane(self, widget):
        pane, szr = self.create_pane(widget)
        self.__b.pack_start(pane)
        szr.connect('dragged', self.cb_resized, len(self.__panes))
        widget.pane_id = len(self.__panes)
        self.__panes.append(pane)
        print self.get_allocation()[3]

    def shrink_pane(self, paneindex):
        
        if paneindex < len(self.__panes):
            oldh = self.__panes[paneindex].get_allocation()[3]
            self.__shrunk[paneindex] = oldh
            self.cb_resized(None, -9999, paneindex)

    def unshrink_pane(self, paneindex):
        if paneindex < len(self.__panes):
            oldh = self.__shrunk.setdefault(paneindex, 200)
            self.cb_resized(None, oldh, paneindex)

    def __rearrange(self):
        pass

    def cb_resized(self, sizer, diff, paneindex):
        pane = self.__panes[paneindex]
        alloc = pane.get_allocation()
        h = alloc.height + diff
        if h < minh:
            h = minh
        diff = h - alloc.height
        if (paneindex + 1) < len(self.__panes):
            lower = self.__panes[paneindex + 1]
            lalloc = lower.get_allocation()
            j = lalloc.height - diff
            if j < minh:
                j = minh
            diff = lalloc.height - j
            lalloc.height = j
            alloc.height = alloc.height + diff
            lower.set_size_request(lalloc.width, lalloc.height)
        
        pane.set_size_request(alloc.width, alloc.height)
             
        self.size_allocate(self.get_allocation())

    def create_pane(self, widget):
        pane = gtk.VBox()
        pane.pack_start(widget)
        szr = sizer()
        pane.pack_start(szr, expand=False)
        return pane, szr

        
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
            return True
        self.connect('map-event', mapped)
        self.set_size_request(-1, 6)

    def cb_release(self, eb, ev):
        self.drag_unhighlight()
        self.grab_remove()
        return True

    def cb_press(self, eb, ev):
        print self.get_pointer()
        self.__y = self.get_pointer()[1]
        print self.__y
        self.drag_highlight()
        self.grab_add()
        return True

    def cb_motion(self, eb, ev):
        x, y = self.get_pointer()
        diff = y - self.__y
        self.emit('dragged', diff)

gobject.type_register(sizer)
    

