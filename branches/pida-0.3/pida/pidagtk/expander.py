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
import gobject
import widgets
        

class expander(gtk.VBox):
    """Expander with sane label management."""

    def __init__(self, right_way_up = True):
        gtk.VBox.__init__(self)
        self.__resizer = widgets.sizer()
        #self.__resizer.connect('dragged', self.cb_resized)
        self.__bodyarea = gtk.EventBox()
        self.__hiddenarea = gtk.EventBox()
        self.__bodywidget = None
        self.__labelarea = gtk.EventBox()
        self.__labelarea.add_events(gtk.gdk.BUTTON_PRESS_MASK |
                                    gtk.gdk.BUTTON_RELEASE_MASK)
        self.__labelarea.connect('button-press-event', self.cb_label_press)
        self.__labelarea.connect('button-release-event', self.cb_label_release)
        self.__labelcontainer = gtk.HBox()
        self.__labelarea.add(self.__labelcontainer)
        self.__arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_ETCHED_IN)
        self.__labelcontainer.pack_start(self.__arrow, expand=False)
        self.__labelholder = gtk.EventBox()
        self.__labelcontainer.pack_start(self.__labelholder)

        #self.pack_start(self.__resizer, expand=False)

        if right_way_up:
            self.pack_start(self.__labelarea, expand=False, padding=0)
            self.pack_start(self.__bodyarea, expand=True, padding=2)
        else:
            self.pack_start(self.__bodyarea, expand=True, padding=2)
            self.pack_start(self.__labelarea, expand=False, padding=0)

        self.waiting = False
        self.populate()
        self.collapse()

    def populate(self):
        pass

    def cb_label_press(self, label, *args):
        pass

    def cb_label_release(self, label, *args):
        self.toggle()

    def cb_resized(self, button, diff):
        if not self.__expanded:
            self.expand()
        else:
            y = self.get_size_request()[1]
            self.set_size_request(-1, y + diff)
        

    def set_label_widget(self, widget):
        self.__labelholder.add(widget)

    def expand(self):
        self.__bodywidget.reparent(self.__bodyarea)
        self.__bodyarea.show_all()
        self.__expanded = True
        self.__arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_IN)
        self.__set_expand(True)

    def collapse(self):
        if self.__bodywidget is not None:
            self.__bodywidget.reparent(self.__hiddenarea)
            self.__bodyarea.hide()
            self.__expanded = False
            self.__arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_ETCHED_IN)
            self.__set_expand(False)

    def __set_expand(self, expand):
        parent = self.get_parent()
        if parent is not None:
            if hasattr(parent, 'set_child_packing'):
                parent.set_child_packing(self, expand=expand, fill=True,
                                     padding=0, pack_type=gtk.PACK_START)
            if hasattr(self, 'pane_id'):
                ggparent = parent.get_parent().get_parent()
                if not expand:
                    ggparent.shrink_pane(self.pane_id)
                else:
                    ggparent.unshrink_pane(self.pane_id)

    def toggle(self):
        def unwait():
            self.waiting = False
        if not self.waiting:
            self.waiting = True
            if self.__expanded:
                self.collapse()
            else:
                self.expand()
            gobject.timeout_add(200, unwait)

    def set_body_widget(self, widget):
        self.__bodywidget = widget
        self.__bodyarea.add(widget)



