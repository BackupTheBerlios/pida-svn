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
import toolbar

class TreeItem(object):
    """An item inside a tree-view."""
    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    def __get_markup(self):
        """Return the markup for the item."""
        return self.__value
    markup = property(__get_markup)

    def __get_key(self):
        """Return the key for the treeview item."""
        return self.__key
    key = property(__get_key)

    def __get_value(self):
        """Return the value for the tree view item."""
        return self.__value
    value = property(__get_value)
    

class Tree(gtk.VBox):
    """A treeiew control with niceness."""
    #The fields for the model.
    FIELDS = (gobject.TYPE_STRING,
              gobject.TYPE_PYOBJECT,
              gobject.TYPE_STRING)

    #The columns for the view.
    COLUMNS = [[gtk.CellRendererText, 'markup', 2]]

    #The signals for the widget.
    __gsignals__ = {'clicked' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'double-clicked' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'right-clicked' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'new-item' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ()),
                    'delete-item' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'edit-item' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,))}
    
    EDIT_BUTTONS = False

    HEADERS_VISIBLE = False

    def __init__(self):
        self.__init_model()
        self.__init_view()
        self.__init_signals()

    def __init_view(self):
        """Load the widgets."""
        gtk.VBox.__init__(self)
        self.__sw = gtk.ScrolledWindow()
        self.pack_start(self.__sw)
        self.__sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__view = gtk.TreeView(self.__model)
        self.__view.set_rules_hint(True)
        self.__sw.add(self.__view)
        self.__view.set_headers_visible(False)
        for column in self.__init_renderers():
            self.__view.append_column(column)
        if self.EDIT_BUTTONS == True:
            self.__toolbar = toolbar.Toolbar()
            self.__toolbar.add_button('new', 'new', 'new', True)
            self.__toolbar.add_button('delete', 'delete', 'delete', True)
            self.__toolbar.add_button('edit', 'edit', 'Edit this item.', True)
            self.pack_start(self.__toolbar, expand=False)
        self.__init_signals()
        self.show_all()

    def __init_model(self):
        """Initialise and return the model for the data."""
        self.__model = gtk.TreeStore(*self.FIELDS)
        return self.__model

    def __init_signals(self):
        def cb_toolbar_clicked(toolbar, action):
            if action == 'new':
                self.emit('new-item')
            elif action == 'delete':
                self.emit('delete-item', self.selected)
            elif action == 'edit':
                self.emit('edit-item', self.selected)
            self.__toolbar.emit_stop_by_name('clicked')
        if self.EDIT_BUTTONS == True:
            self.__toolbar.connect('clicked', cb_toolbar_clicked)
        def cb_cursor_changed(view):
            self.emit('clicked', self.selected)
            self.__view.emit_stop_by_name('cursor-changed')
        self.__view.connect('cursor-changed', cb_cursor_changed)
        def cb_row_activated(view, path, column):
            self.emit('double-clicked', self.selected)
            self.__view.emit_stop_by_name('row-activated')
        self.__view.connect_after('row-activated', cb_row_activated)
        def cb_button_press_event(source, event):
            if event.button == 3:
                pathinf = self.__view.get_path_at_pos(int(event.x), int(event.y))
                if pathinf is not None:
                    path, col, cellx, celly = pathinf
                    self.__view.grab_focus()
                    self.__view.set_cursor(path, None, 0)
                    self.__view.emit_stop_by_name('button-press-event')
                    self.emit('right-clicked', self.selected)
        self.__view.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.__view.connect('button-press-event', cb_button_press_event)

    def __init_renderers(self):
        """Initialise the renderers."""
        for renderer_type, attribute, field in self.COLUMNS:
            renderer = renderer_type()
            renderer.set_property('ypad', 1)
            column = gtk.TreeViewColumn(attribute, renderer,
                                        **{attribute:field})
            column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
            yield column

    def add_item(self, item, parent=None):
        """Add an item to the tree."""
        markup = item.markup
        return self.model.append(parent, [item.key, item, markup])
    
    def add_items(self, items):
        """Add items to the tree."""
        for item in items:
            self.add_item(item)

    def clear(self):
        """Clear the tree."""
        self.__model.clear()

    def set_items(self, items):
        """Set the items in the tree from the item list."""
        self.clear()
        self.add_items(items)

    def __get_model(self):
        """Return the Tree Model."""
        return self.__model
    model = property(__get_model)
    
    def __get_selected(self, column=1):
        """Get the selected item."""
        ite = self.__get_selected_iter()
        if ite:
            return self.__get(ite, column)
    selected = property(__get_selected)

    def set_selected(self, key):
        """Set the selected item to the first item matching the key."""
        for row in self.model:
            if row[0] == key:
                self.__view.set_cursor(row.path)
                return True
        return False

    def __get_selected_iter(self):
        """Get the selected Tree Model Iter."""
        path = self.__get_selected_path()
        if path:
            return self.__model.get_iter(path)
        
    def __get_selected_path(self):
        """Get the selected Tree View Path."""
        return self.__view.get_cursor()[0]

    def __get(self, niter, column):
        """Get a cell's vlue from the Tree Model."""
        return self.__model.get_value(niter, column)
    get = __get

    def __set(self, niter, column, value):
        self.__model.set_value(niter, column, value)
    set = __set

class IconTreeItem(TreeItem):
    """I tree item with an icon."""
    def __init__(self, key, value, image=None, icon_filename=None):
        TreeItem.__init__(self, key, value)
        if image is not None:
            self.__image = image
        elif icon_filename is not None:
            self.__image = gtk.Image()
            self.__image.set_from_file(icon_filename)
        else:
            self.__image = gtk.Image()

    def get_icon(self):
        return self.__image
    icon = property(get_icon)

    def get_pixbuf(self):
        return self.icon.get_pixbuf()
    pixbuf = property(get_pixbuf)


class IconTree(Tree):
    """Tree with icons.""" 
    FIELDS = (gobject.TYPE_STRING,
              gobject.TYPE_PYOBJECT,
              gobject.TYPE_STRING,
              gtk.gdk.Pixbuf)
    
    COLUMNS = [[gtk.CellRendererPixbuf, 'pixbuf', 3],
               [gtk.CellRendererText, 'markup', 2]]

    def add_item(self, item, parent=None):
        markup = item.markup
        pixbuf = item.pixbuf
        return self.model.append(parent, [item.key, item, markup, pixbuf])
        
# Don't forget to register
gobject.type_register(Tree)

def test():
    w = gtk.Window()
    t = Tree()
    w.add(t)
    w.show_all()
    ti = TreeItem("banana", 'banan')
    t.add_item(ti)
    gtk.main()

def clicked(obj, o2):
    print obj, o2.markup

import sys

class dummy_stdout(object):

    def __init__(self, tv):
        self.tv = tv

    def write(self, data):
        self.tv.get_buffer().insert_at_cursor(data)

    def flush(self):
        pass


def test_icon():
    w = gtk.Window()
    v = gtk.VBox()
    w.add(v)
    t = Tree()
    t.connect('right-clicked', clicked)
    v.pack_start(t)
    e = gtk.TextView()
    v.pack_start(e)
    sys.stdout = dummy_stdout(e)
    print "hello"
    w.show_all()
    im = gtk.Image()

    fn = "/usr/share/icons/hicolor/24x24/stock/generic/stock_book_open.png"
    im.set_from_file(fn)
    ti = TreeItem("banana", 'banan')
    t2 = TreeItem("b", 'bananass')
    t.set_items([ti, t2])
    print t.set_selected('b')
    gtk.main()

if __name__ == '__main__':
    test_icon()
