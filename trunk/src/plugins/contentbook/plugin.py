# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id: plugin.py 454 2005-07-24 16:08:40Z aafshar $
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
import pida.configuration.registry as registry
import pida.configuration.config as config
import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.base as base


class IPageObject(base.pidaobject):

    win = None
    icon = None

    def start(self):
        pass

    def die(self):
        pass

class TabLabel(base.pidaobject):
    """ A label for a notebook tab. """
    def do_init(self, stockid):
        # Construct widgets
        self.win = gtk.EventBox()
        
        #self.set_visible_window(True)
        # Get the requested icon
        self.image = self.do_get_image(stockid)
        self.win.add(self.image)
        # Different styles for highligting labels
        self.hst = self.win.style.copy()
        self.dst = self.win.style
        col = self.win.get_colormap().alloc_color('#FF8080')
        for i in xrange(5):
            self.hst.bg[i] = col
        self.win.show_all()

    def read(self):
        """ Called to unhighlight the tab label """
        self.set_style(self.dst)
   
    def unread(self):
        """ Highlight the tab label """
        self.set_style(self.hst)


class Plugin(plugin.Plugin):

    """ The content area plugin """
    NAME = "Content"
    DETACHABLE = True

    def populate_widgets(self):
        self.pages = {}
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.set_scrollable(True)
        self.notebook.set_property('show-border', False)
        self.notebook.set_property('tab-border', 2)
        self.notebook.set_property('enable-popup', True)
        self.add(self.notebook)
        self.add_separator()

        #self.add_button('python', self.cb_python,
        #                'Open a python shell')


        def browse(*args):
            self.do_action('newbrowser')
        self.add_button('internet', browse,
                        'Open a new browser')
        #self.add_button('terminal', self.cb_new,
        #                'Open a new shell')
        self.add_button('close', self.cb_toolbar_close,
                        'Close current tab.')
       
        self.panes = {}
        self.toolbar_popup.add_separator()
        #self.toolbar_popup.add_item('configure',
        #                    'Configure this shortcut bar',
        #                    self.cb_conf_clicked, [])

    def configure(self, reg):
        ### Terminal emulator options
        
        self.registry = reg.add_group('content_pane',
            'Options for the built in terminal emulator.')

              
        self.registry.add('on_top',
                registry.Boolean,
                False,
                'Is the detached window on top of main PIDA window? (Transient'
                ' window)')

    def add_page(self, pageobj):
        label = TabLabel(pageobj.icon)
        self.notebook.append_page(pageobj.win, tab_label=label.win)
        pageobj.start()
        if self.detach_window:
            self.detach_window.present()
        pageobj.win.show_all()
        self.pages[pageobj.win] = pageobj
        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)

    
    def remove_page(self, index):
        child = self.notebook.get_nth_page(index)
        if child:
            self.pages[child].die()
            self.notebook.remove_page(index)
        return True
        
    def remove_current_page(self):
        if not self.remove_page(self.notebook.get_current_page()):
            self.error('cannot remove log window')

    def cb_toolbar_clicked(self, button, args):
        pass

    def cb_toolbar_close(self, button):
        self.remove_current_page()

    def evt_contentpage(self, pageobj):
        self.add_page(pageobj)

    def evt_closecontentpage(self):
        self.remove_current_page()
