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
import icons
import toolbar

TITLE_MU = """<span size="small" weight="bold">%s</span>"""
       
class ContentView(gtk.VBox):

    __gsignals__ = {'action' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT,)),
                    'removed' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        ())}

    ICON = 'terminal'
    ICON_TEXT = ''

    HAS_DETACH_BUTTON = True
    HAS_CLOSE_BUTTON = True
    HAS_LABEL = True

    def __init__(self, icon=None, text=''):
        gtk.VBox.__init__(self)
        if icon is None:
            icon = self.ICON
        if text == '':
            text = self.ICON_TEXT
        barbox = gtk.HBox()
        self.pack_start(barbox, expand=False)
        self.__toolbar = toolbar.Toolbar()
        barbox.pack_start(self.__toolbar, expand=False, fill=False)
        self.__toolbar.connect('clicked', self.cb_toolbar_clicked)
        self.__title = gtk.Label()
        self.set_title(text)
        if self.HAS_LABEL:
            barbox.pack_start(self.__title)
        if self.HAS_DETACH_BUTTON or self.HAS_CLOSE_BUTTON:
            barbox.pack_start(gtk.VSeparator(), expand=False)
        self.__controlbar = toolbar.Toolbar()
        barbox.pack_start(self.__controlbar, expand=False, fill=False)
        self.__controlbar.connect('clicked', self.cb_controlbar_clicked)
        if self.HAS_DETACH_BUTTON:
            self.__controlbar.add_button('detach', 'fullscreen',
                                         'detach this window')
        if self.HAS_CLOSE_BUTTON:
            self.__controlbar.add_button('close', 'close',
                                         'close this window')
        self.__icon = icon
        self.__parent = None
        self.populate()

    def populate(self):
        pass

    def add_button(self, name, icon, doc):
        button = self.__toolbar.add_button(name, icon, doc)
        self.show_all()

    def add_menu(self):
        pass

    def add_menuitem(self):
        pass

    def detach(self):
        if self.__parent is None:
            self.__parent = ContentHolderWindow(self)
        else:
            self.reattach()

    def reattach(self):
        if self.__parent is not None:
            self.__parent.remove(self)
            self.__parent.hide_all()
            self.__parent = None
            self.contentbook.append_page(self)

    def cb_toolbar_clicked(self, toolbar, name):
        self.emit('action', name)

    def cb_controlbar_clicked(self, toolbar, name):
        if name == 'detach':
            self.detach()
        elif name == 'close':
            self.close()
            print 'close'
        else:
            print name
        pass#self.emit('action', name)

    def close(self):
        if hasattr(self, 'contentbook'):
            self.contentbook.remove_page(self)

    def cb_switch(self, button):
        if hasattr(self, 'contentbook'):
            self.contentbook.set_page(self)

    def raise_tab(self):
        if hasattr(self, 'contentbook'):
            self.contentbook.set_page(self)

    def get_tab_label(self):
        return icons.icons.get_image(self.__icon)
    icon = property(get_tab_label)

    def set_title(self, title):
        self.__title.set_markup(TITLE_MU % title)
    

class ContentBook(ContentView):
    
    HAS_CLOSE_BUTTON = False
    HAS_DETACH_BUTTON = False
    HAS_LABEL = False

    TABS_VISIBLE = True

    def __init__(self, *args, **kwargs):
        ContentView.__init__(self, *args, **kwargs)
        self.__notebook = gtk.Notebook()
        self.pack_start(self.__notebook)
        self.__notebook.set_tab_pos(gtk.POS_TOP)
        self.__notebook.set_scrollable(True)
        self.__notebook.set_show_border(False)
        self.__notebook.set_show_tabs(self.TABS_VISIBLE)
        self.__notebook.set_property('tab-border', 2)
        self.__notebook.set_property('homogeneous', True)
        self.__notebook.set_property('enable-popup', True)
        self.__notebook.set_show_border(False)
    
    def build_tab_label(self, contentview):
        return contentview.icon

    def append_page(self, contentview):
        self.__notebook.append_page(contentview,
                                    tab_label=self.build_tab_label(contentview))
        contentview.contentbook = self
        self.__notebook.show_all()
        self.set_page(contentview)

    def set_page(self, contentview):
        pagenum = self.__notebook.page_num(contentview)
        self.__notebook.set_current_page(pagenum)

    def remove_page(self, contentview):
        contentview.emit('removed')
        pagenum = self.__notebook.page_num(contentview)
        self.__notebook.remove_page(pagenum)

    def __get_notebook(self):
        return self.__notebook
    notebook = property(__get_notebook)

class ContentHolderWindow(gtk.Window):
    
    def __init__(self, child):
        gtk.Window.__init__(self)
        self.__child = child
        self.__child.reparent(self)
        self.connect('destroy', self.cb_destroy)
        self.show_all()

    def cb_destroy(self, window):
        if self.__child is not None:
            self.__child.reattach()
            self.__child = None

class ContentBookInSlider(ContentBook):

    def append_page(self, contentview):
        ContentBook.append_page(self, contentview)
        self.resize_third()

    def remove_page(self, contentview):
        ContentBook.remove_page(self, contentview)
        if self.notebook.get_n_pages() == 0:
            self.shrink_force()

    def shrink_force(self):
        self.slider.set_property('position-set', False)
        self.shrink()

    def shrink(self):
        self.resize(self.slider_max)
        self.slider.set_property('position-set', False)

    def resize_half(self):
        self.resize(self.slider_max / 2)

    def resize_third(self):
        self.resize(self.slider_max / 1.5)

    def resize(self, position):
        if self.slider.get_property('position-set') == False:
            self.slider.set_position(position)

    def get_slider_max(self):
        if hasattr(self, 'slider'):
            return self.slider.get_property('max_position')
        else:
            return None

    slider_max = property(get_slider_max)

class EditorView(ContentView):

    def __init__(self, editor_widget):
        ContentView.__init__(self)
        self.pack_start(editor_widget)
        self.editor = editor_widget
        self.add_button('save', 'save', 'Save the current file.')
        self.add_button('undo', 'undo', 'Undo the last change.')

if __name__ == '__main__':
    w = gtk.Window()
    c = ContentView(text="hello")
    w.add(c)
    w.show_all()
    gtk.main()
