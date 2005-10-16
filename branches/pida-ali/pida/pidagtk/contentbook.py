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
class IContentPage:

    pass


class ContenttabLabel(gtk.HBox):

    def __init__(self, icon, text):
        gtk.HBox.__init__(self)
        icon = icons.icons.get_image(icon)
        closebut = icons.icons.get_button('close', 'close this tab')
        label = gtk.Label()
        label.set_markup('<span size="small">%s</span>' % text)
        self.pack_start(icon, padding=2)
        self.pack_start(label)
        self.pack_start(closebut)
        self.show_all()
        self.close_button = closebut
       
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
    ICON_TYPE = ContenttabLabel
    ICON_TEXT = ''

    def __init__(self, icon=None, text=''):
        gtk.VBox.__init__(self)
        self.__toolbar = toolbar.Toolbar()
        self.pack_start(self.__toolbar, expand=False, fill=False)
        self.__toolbar.connect('clicked', self.cb_toolbar_clicked)
        if icon is None:
            icon = self.ICON
        if text == '':
            text = self.ICON_TEXT
        self.__icon = self.ICON_TYPE(icon, text)
        if hasattr(self.__icon, 'close_button'):
            self.__icon.close_button.connect('clicked', self.cb_close)
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

    def cb_toolbar_clicked(self, toolbar, name):
        self.emit('action', name)

    def cb_close(self, button):
        if hasattr(self, 'contentbook'):
            self.contentbook.remove_page(self)

    def raise_tab(self):
        if hasattr(self, 'contentbook'):
            self.contentbook.set_page(self)

    def get_tab_label(self):
        return self.__icon
    tablabel = property(get_tab_label)
    

class ContentBook(ContentView):
    
    def __init__(self, *args, **kwargs):
        ContentView.__init__(self, *args, **kwargs)
        self.__notebook = gtk.Notebook()
        self.pack_start(self.__notebook)
        self.__notebook.set_tab_pos(gtk.POS_TOP)
        self.__notebook.set_scrollable(True)
        self.__notebook.set_property('show-border', False)
        self.__notebook.set_property('tab-border', 2)
        self.__notebook.set_property('homogeneous', True)
        self.__notebook.set_property('enable-popup', True)
        self.__notebook.set_show_border(False)
    
    def append_page(self, contentview):
        self.__notebook.append_page(contentview, tab_label=contentview.tablabel)
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
