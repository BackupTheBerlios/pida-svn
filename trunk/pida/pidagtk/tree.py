# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

#Copyright (c) 2005 The PIDA Project

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

# pidagtk import(s)
import toolbar
from pida.utils.kiwiutils import gsignal, gproperty


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

    
class QuestionBox(gtk.HBox):

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


class Tree(gtk.VBox):
    """A treeview control with niceness."""
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
                        (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)),
                    'middle-clicked' : (
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
                        ()),
                    'edit-item' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

    gproperty('has-edit-box', bool, default=True)
    gproperty('headers-visible', bool, default=True)
    gproperty('icons-visible', bool, default=False)
    gproperty('markup-format-string', str, default='%(key)s')

    def do_get_property(self, prop):
        return self.__properties.setdefault(prop.name, prop.default_value)

    def do_set_property(self, prop, value):
        self.__properties[prop.name] = value

    EDIT_BUTTONS = False
    EDIT_BOX = False

    HEADERS_VISIBLE = False

    SORT_BY = None
    SORT_LIST = None
    SORT_AVAILABLE = None
    SORT_CONTROLS = False

    def __init__(self):
        self.__init_model()
        self.__init_view()
        self.__init_signals()
        self.__properties = {}

    def __init_view(self):
        """Load the widgets."""
        gtk.VBox.__init__(self)
        self.__sw = gtk.ScrolledWindow()
        self.pack_start(self.__sw)
        self.__sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.__view = gtk.TreeView(self.__model)
        self.__view.set_rules_hint(True)
        self.__view.set_enable_search(False)
        self.__view.set_model(self.__model)
        self.__sw.add(self.__view)
        self.__view.set_headers_visible(False)
        for column in self.__init_renderers():
            self.__view.append_column(column)
        if self.SORT_CONTROLS == True:
            sb = gtk.Expander()
            self.pack_start(sb, expand=False)
            l = gtk.Label('Sort')
            sb.set_label_widget(l)
            hb = gtk.HBox()
            sb.add(hb)
            self.__sortcombo = gtk.combo_box_new_text()
            hb.pack_start(self.__sortcombo)
            self.__sortcombo.connect('changed', self.cb_sortcombo_changed)
            if self.SORT_AVAILABLE is not None:
                self.sort_available = dict(self.SORT_AVAILABLE)
                for attr, val in self.SORT_AVAILABLE:
                    self.__sortcombo.append_text(attr)
            self.__sortcombo.set_active(0)
        if self.EDIT_BOX == True:
            self.__editbox = QuestionBox()
            self.pack_start(self.__editbox, expand=False)
        if self.EDIT_BUTTONS == True:
            self.__toolbar = toolbar.Toolbar()
            self.__toolbar.add_button('new', 'new', 'new', True)
            self.__toolbar.add_button('delete', 'delete', 'delete', True)
            self.__toolbar.add_button('edit', 'edit', 'Edit this item.', True)
            self.__toolbar.connect('clicked', self.cb_toolbar_clicked)
            self.pack_start(self.__toolbar, expand=False)
        self.__init_signals()
        if self.SORT_BY is not None:
            self.sort_by([self.SORT_BY])
        if self.SORT_LIST is not None:
            self.sort_by(self.SORT_LIST)
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
                self.emit('delete-item')
            elif action == 'edit':
                self.emit('edit-item')
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
                self.__view.emit_stop_by_name('button-press-event')
                if pathinf is not None:
                    path, col, cellx, celly = pathinf
                    self.__view.grab_focus()
                    self.__view.set_cursor(path, None, 0)
                    self.emit('right-clicked', self.selected, event)
                else:
                    self.emit('right-clicked', None, event)
                return True
            if event.button == 2:
                pathinf = self.__view.get_path_at_pos(int(event.x), int(event.y))
                if pathinf is not None:
                    path, col, cellx, celly = pathinf
                    self.__view.grab_focus()
                    self.__view.set_cursor(path, None, 0)
                    self.__view.emit_stop_by_name('button-press-event')
                    self.emit('middle-clicked', self.selected)
                    return True
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

    def add_item(self, item, key=None, parent=None):
        """Add an item to the tree."""
        if key is None:
            key = item.key
        else:
            item.key = key
        titem = TreeItem(key, item)
        row = [key, titem, self.__get_markup(item)]
        niter = self.model.append(parent, row)
        def reset():
            self.model.set_value(niter, 2, self.get_markup(item))
        titem.reset_markup = reset
        item.reset_markup = reset
        return niter

    def __get_markup(self, item):
        unmangled = {}
        markup_fmt = self.get_property('markup-format-string')
        for k in dir(item):
            if k in markup_fmt:
                unmangled[k] = getattr(item, k)
        markup_string = markup_fmt % unmangled
        return markup_string
    get_markup = __get_markup
    
    def add_items(self, items):
        """Add items to the tree."""
        for item in items:
            self.add_item(item)

    def clear(self):
        """Clear the tree."""
        self.__model.clear()

    def del_item(self):
        """Removes the currently selected item from the tree."""
        selected_path = self.__get_selected_path()
        if selected_path:
            self.__model.emit('row-deleted', selected_path)
        
    def set_items(self, items):
        """Set the items in the tree from the item list."""
        self.clear()
        self.add_items(items)

    def question(self, callback, prompt):
        self.__editbox.question(callback, prompt)

    def sort_by(self, attrnames, sortcolid=0, columnid=1):
        def comparemethod(model, iter1, iter2):
            v1 = model.get_value(iter1, columnid)
            v2 = model.get_value(iter2, columnid)
            def cmpvs(attrname, v1, v2):
                attr1 = attr2 = None
                if v1 is not None:
                    attr1 = getattr(v1.value, attrname, None)
                if v2 is not None:
                    attr2 = getattr(v2.value, attrname, None)
                if attr1 is None:
                    return -1
                elif attr2 is None:
                    return 1
                else:
                    return cmp(attr2, attr1)
            for attrname in attrnames:
                compd = cmpvs(attrname, v1, v2)
                if compd != 0:
                    return compd
            return 0
        self.__model.set_sort_func(sortcolid, comparemethod)
        self.__model.set_sort_column_id(sortcolid, gtk.SORT_DESCENDING)

    def sort_by_list(self, attrnames, columnid=1):
        for i, attrname in enumerate(attrnames):
            self.sort_by(attrname, i, columnid)
        self.__model.set_sort_column_id(0, gtk.SORT_DESCENDING)

    def __get_model(self):
        """Return the Tree Model."""
        return self.__model
    model = property(__get_model)

    def __get_view(self):
        return self.__view
    view = property(__get_view)
    
    def __get_selected(self, column=1):
        """Get the selected item."""
        ite = self.__get_selected_iter()
        if ite:
            return self.__get(ite, column)
    selected = property(__get_selected)
    
    def get_selected_key(self):
        return self.__get_selected(0)
    selected_key = property(get_selected_key)

    def set_selected(self, key):
        """Set the selected item to the first item matching the key."""
        key = str(key)
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
    selected_iter = property(__get_selected_iter)
        
    def __get_selected_path(self):
        """Get the selected Tree View Path."""
        return self.__view.get_cursor()[0]
    selected_path = property(__get_selected_path)

    def __get(self, niter, column):
        """Get a cell's vlue from the Tree Model."""
        return self.__model.get_value(niter, column)
    get = __get

    def __set(self, niter, column, value):
        self.__model.set_value(niter, column, value)
    set = __set

    def cb_toolbar_clicked(self, toolbar, action):
        if action == 'new':
            self.emit('new-item')
        elif action == 'edit':
            self.emit('edit-item')
        elif action == 'delete':
            self.emit('delete-item')
        toolbar.emit_stop_by_name('clicked')

    def cb_sortcombo_changed(self, combo):
        text = combo.get_active_text()
        self.sort_by([self.sort_available[text]])

gobject.type_register(Tree)

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
        return getattr(self.icon, 'get_pixbuf', lambda: self.icon)()
    pixbuf = property(get_pixbuf)


class IconTree(Tree):
    """Tree with icons.""" 
    FIELDS = (gobject.TYPE_STRING,
              gobject.TYPE_PYOBJECT,
              gobject.TYPE_STRING,
              gtk.gdk.Pixbuf)
    
    COLUMNS = [[gtk.CellRendererPixbuf, 'pixbuf', 3],
               [gtk.CellRendererText, 'markup', 2]]

    def add_item(self, item, key=None, parent=None):
        pixbuf = item.pixbuf
        if key is None:
            key = item.key
        else:
            item.key = key
        titem = TreeItem(key, item)
        row = [key, titem, self.get_markup(item), pixbuf]
        niter = self.model.append(parent, row)
        def reset():
            self.model.set_value(niter, 2, self.get_markup(item))
        titem.reset_markup = reset
        item.reset_markup = reset
        return niter

class ToggleTree(Tree):

    FIELDS = (gobject.TYPE_STRING,
              gobject.TYPE_PYOBJECT,
              gobject.TYPE_STRING,
              gobject.TYPE_BOOLEAN)
    
    COLUMNS = [[gtk.CellRendererText, 'markup', 2],
               [gtk.CellRendererToggle, 'active', 3] ]

    
    def add_item(self, item, key=None, parent=None):
        active = item.active
        if key is None:
            key = item.key
        else:
            item.key = key
        titem = TreeItem(key, item)
        row = [key, titem, self.get_markup(item), active]
        niter = self.model.append(parent, row)
        def reset():
            self.model.set_value(niter, 2, self.get_markup(item))
            self.model.set_value(niter, 3, item.active)
        titem.reset_markup = reset
        item.reset_markup = reset
        return niter

def test():
    w = gtk.Window()
    v = gtk.VBox()
    w.add(v)
    t = Tree()
    v.pack_start(t)
    b = gtk.Button('foo')
    v.pack_start(b, False)
    w.show_all()

    def _clicked(button):
        t.selected.value.key = 'ali'
        t.selected.reset_markup()
    b.connect('clicked', _clicked)

    class Dummy(object):
        key = "fooood"
        name = 'mess'
    for i in range(20):
        d = Dummy()
        t.add_item(d)

    gtk.main()

