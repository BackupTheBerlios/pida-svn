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

class Tree(object):
    ''' A custom treeview subclass that is used throughout Pida. '''
    COLUMNS = [('name', gobject.TYPE_STRING, gtk.CellRendererText, True,
                'markup')]
    SCROLLABLE = True
    XPAD = 0
    YPAD = 1

    def __init__(self, cb):
        self.cb = cb
        self.model = gtk.TreeStore(*[l[1] for l in self.COLUMNS])
        self.view = gtk.TreeView(self.model)
        self.view.set_headers_visible(False)
        self.view.set_rules_hint(True)
        self.win = gtk.VBox()

        self.toolbar = gtk.HBox()
        self.win.pack_start(self.toolbar, expand=False, padding=4)

        if self.SCROLLABLE:
            sw = gtk.ScrolledWindow()
            self.win.pack_start(sw)
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            sw.add(self.view)
        else:
            self.win.pack_start(self.view)
        i = 0
        for (name, typ, rendtype, vis, attr) in self.COLUMNS:
            if vis:
                renderer = rendtype()
                renderer.set_property('ypad', self.YPAD)
                renderer.set_property('xpad', self.XPAD)
                attrdict = {attr:i}
                column = gtk.TreeViewColumn(name, renderer, **attrdict)
                #column.set_expand(False)
                column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
                self.view.append_column(column)
            i = i + 1

        self.r_cb_activated = None
        self.view.connect('row-activated', self.cb_activated)
        self.r_cb_selected = None
        self.view.connect('cursor-changed', self.cb_selected)
        self.r_cb_rightclick = None
        self.view.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.view.connect('button-press-event', self.cb_butpress)


        self.view.columns_autosize()
        self.init()
    
    def init(self):
        ''' Called by the constructor, for overriding. '''
        pass

    def add_item(self, data, parent=None):
        ''' Add an item to the tree view's model. '''
        return self.model.append(parent, data)

    def clear(self):
        ''' Clear the View. '''
        self.model.clear()

    def connect_select(self, cb):
        ''' Connect the external single-click handler. '''
        self.r_cb_selected = cb

    def connect_activate(self, cb):
        ''' Connect the external activate handler. '''
        self.r_cb_activated = cb

    def connect_rightclick(self, cb):
        ''' Connect the external right-click handler. '''
        self.r_cb_rightclick = cb

    def cb_activated(self, *args):
        if self.l_cb_activated(*args) and self.r_cb_activated:
            self.r_cb_activated(*args)

    def cb_butpress(self, source, event):
        if event.button == 3:
            path, dd = self.view.get_dest_row_at_pos(int(event.x),
                                                        int(event.y))
            ite = self.model.get_iter(path)
            self.cb_rightclick(ite, event.time)

    def cb_selected(self, *args):
        if self.l_cb_selected(*args) and self.r_cb_selected:
            self.r_cb_selected(*args)

    def cb_rightclick(self, *args):
        if self.l_cb_rightclick(*args) and self.r_cb_rightclick:
            self.r_cb_rightclick(*args)

    def l_cb_activated(self, tv, path, arg):
        return True

    def l_cb_selected(self, tv):
        return True

    def l_cb_rightclick(self, ite, time):
        return True

    def update(self):
        self.view.set_model(self.model)

    def selected(self, column):
        ite = self.selected_iter()
        if ite:
            return self.get(ite, column)

    def selected_iter(self):
        path = self.view.get_cursor()[0]
        if path:
            return self.model.get_iter(path)
        
    def selected_path(self):
        return self.view.get_cursor()[0]

    def get(self, niter, column):
        return self.model.get_value(niter, column)

    def toggle_expand(self, path):
        niter = self.model.get_iter(path)
        if self.model.iter_has_child(niter):
            if self.view.row_expanded(path):
                self.view.collapse_row(path)
            else:
                self.view.expand_row(path, False)

