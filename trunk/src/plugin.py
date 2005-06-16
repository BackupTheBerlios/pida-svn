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

"""This module provides the base plugin superclass"""

# GTK import
import gtk

# Pida import
import gtkextra

class Plugin(object):
    # Class attributes for overriding.
    # The name of the plugin.
    NAME = 'Plugin'
    # The icon in the top left
    ICON = 'fullscreen'
    # The alternative icon for tabs and tooltip
    DICON = 'fullscreen', 'Detach window.'
    # Whether the plugin is detachable.
    DETACHABLE = False

    def __init__(self, cb):
        """ Build the plugin. """
        # Instance of the Application class.
        self.cb = cb
        # The main box.
        self.win = gtk.VBox()
        self.win.show()
        # The tool bar.        
        self.bar = gtk.HBox()
        self.win.pack_start(self.bar, expand=False)
        self.bar.show()
        ## The control bar.
        self.ctlbar = gtk.HBox()
        self.bar.pack_start(self.ctlbar)
        self.ctlbar.show()
        # detach button
        eb = gtk.EventBox()
        self.dtbut = gtk.ToggleToolButton(stock_id=None)
        eb.add(self.dtbut)
        self.ctlbar.pack_start(eb, expand=False)
        ic = self.cb.icons.get_image(self.DICON[0], 10)
        self.dtbut.set_icon_widget(ic)
        self.dtbut.connect('toggled', self.cb_toggledetatch)
        self.cb.tips.set_tip(eb, self.DICON[1])
        # The main title label.
        self.label = gtk.Label(self.NAME)
        self.ctlbar.pack_start(self.label, expand=False)
        # The horizontal expander.
        self.sepbar = gtkextra.Sepbar(self.cb)
        self.sepbar.connect(self.cb_sep_rclick, self.cb_sep_dclick)
        self.ctlbar.pack_start(self.sepbar.win, padding=6)
        # The shortcut bar.
        self.shortbar = gtk.HBox()
        self.bar.pack_start(self.shortbar, expand=False)
        # The custom tool bar.
        self.cusbar = gtkextra.Toolbar(self.cb)
        self.bar.pack_start(self.cusbar.win, expand=False)
        # The holder for transient windows.
        self.transwin = gtk.VBox()
        self.transwin.show()
        self.win.pack_start(self.transwin, expand=False)
        #message dialog
        self.msgbox = gtkextra.Messagebox(self.cb)
        self.transwin.pack_start(self.msgbox.win, expand=False)
        #question dialog
        self.qstbox = gtkextra.Questionbox(self.cb)
        self.transwin.pack_start(self.qstbox.win, expand=False)
        # The option dialog
        self.optbox = gtkextra.Optionbox(self.cb)
        self.transwin.pack_start(self.optbox.win, expand=False)
        # The content area.
        self.frame = gtk.VBox()
        self.win.pack_start(self.frame)
        # The toolbar popup menu.
        self.toolbar_popup = gtkextra.Popup(self.cb)
        self.populate_widgets()
        self.connect_widgets()
        self.frame.show_all()
        self.win.show_all()

    def cb_sep_rclick(self, event):
        self.toolbar_popup.popup(event.time)

    def cb_sep_dclick(self, event):
        pass

    def populate_widgets(self):
        pass

    def connect_widgets(self):
        pass

    def message(self, message):
        self.msgbox.message(message)

    def question(self, message, callback):
        self.qstbox.question(message, callback)

    def option(self, message, opts, callback):
        self.optbox.option(message, opts, callback)

    def query(self, message, options, callback):
        if len(options):
            self.option(message, options, callback)
        else:
            self.question(message, callback)

    def attach(self, *a):
        self.win.reparent(self.oldparent)
        self.dwin.destroy()
    
    def detatch(self):
        self.oldparent = self.win.get_parent()
        self.dwin = Winparent(self.cb, self)

    def add(self, widget, *args, **kwargs):
        self.frame.pack_start(widget, *args, **kwargs)

    def add_button(self, stock, callback, tooltip='None Set!', cbargs=[]):
        self.toolbar_popup.add_item(stock, tooltip, callback, cbargs)
        return self.cusbar.add_button(stock, callback, tooltip, cbargs)
    
    def add_separator(self):
        self.toolbar_popup.add_separator()
        self.cusbar.add_separator()
        
    def cb_alternative(self):
        pass
    
    def cb_sepbar_rclick(self):
        pass

    def cb_sepbar_rclick(self):
        pass

    def cb_toggledview(self, *a):
        self.check_visibility()
    
    def cb_toggledetatch(self, *a):
        if self.dtbut.get_active():
            if self.DETACHABLE:
                self.detatch()
            else:
                self.cb_alternative()
                self.dtbut.set_active(False)
        else:
            if self.DETACHABLE:
                self.attach()
        
    def cb_shrink(self, *a):
        self.shrink()

    def cb_grow(self, *a):
        self.grow()

    def grow(self):
        nh = self.win.size_request()[1] + 64
        nh = 64 * divmod(nh, 64)[0]
        self.win.set_size_request(-1, nh)       

    def shrink(self):
        nh = self.win.size_request()[1] - 64
        if nh < 64:
            nh = 64
        else:
            nh = 64 * divmod(nh, 64)[0]
        self.win.set_size_request(-1, nh)      

    def check_visibility(self):
        #self.set_visibility(not self.vtbut.get_active())
        self.set_visibility(True)
    
    def set_visibility(self, visible):
        if visible:
            self.show()
        else:
            self.hide()
        self.ctlbar.show_all()

    def hide(self):
        self.frame.hide_all()
        #self.frame.set_size_request(0, 0)
        self.cusbar.hide_all()
        #self.vtbut.set_icon_widget(self.vtgicon)

    def show(self):
        self.frame.show_all()
        #self.frame.set_size_request(-1, -1)
        self.cusbar.show_all()
        #self.vtbut.set_icon_widget(self.vtsicon)
    
    def log(self, message, level):
        text = '%s: %s' % (self.NAME, message)
        self.cb.action_log(self.NAME, message, level)

    def debug(self, message):
        self.log(message, 0)

    def info(self, message):
        self.log(message, 1)

    def warn(self, message):
        self.log(message, 2)

    def error(self, message):
        self.log(message, 3)

    def evt_init(self):
        self.msgbox.hide()
        self.optbox.hide()
        self.qstbox.hide()
