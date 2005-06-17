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
    """ The base plugin class. """
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
        # The content area.
        self.frame = gtk.VBox()
        self.win.pack_start(self.frame)
        # The toolbar popup menu.
        self.toolbar_popup = gtkextra.Popup(self.cb)
        self.populate_widgets()
        self.connect_widgets()
        self.frame.show_all()
        self.win.show_all()

    def populate_widgets(self):
        """ Called after the constructor to populate the plugin.
        
        Override this method and add the desired widgets to the plugin.
        """
        pass

    def connect_widgets(self):
        """ Called after widget population to connect signals. """
        pass

    def add(self, widget, *args, **kwargs):
        """ Add a widget to the plugin. """
        self.frame.pack_start(widget, *args, **kwargs)

    def add_button(self, stock, callback, tooltip='None Set!', cbargs=[]):
        """ Add a button to the pluugin toolbar and toolbar menu. """
        self.toolbar_popup.add_item(stock, tooltip, callback, cbargs)
        return self.cusbar.add_button(stock, callback, tooltip, cbargs)
    
    def add_separator(self):
        """ Add a separator to the toolbar and toolbar menu. """
        self.toolbar_popup.add_separator()
        self.cusbar.add_separator()
        
    def message(self, message):
        """ Give the user a message in a transient window. """
        self.msgbox.message(message)

    def question(self, message, callback):
        """ Ask the user a question in a transient window. """
        self.qstbox.question(message, callback)

    def attach(self, *a):
        """ Reparent the plugin in the original parent. """
        self.win.reparent(self.oldparent)
        self.dwin.destroy()
    
    def detatch(self):
        """ Reparent the plugin in a top-level window. """
        self.oldparent = self.win.get_parent()
        self.dwin = gtkextra.Winparent(self.cb, self)

    def log(self, message, level):
        """ Log a message. """
        # Add plugin name to message.
        text = '%s: %s' % (self.NAME, message)
        self.cb.action_log(self.NAME, message, level)

    def debug(self, message):
        """ Log a debug message. """
        self.log(message, 0)

    def info(self, message):
        """ Log an info message. """
        self.log(message, 1)

    def warn(self, message):
        """ Log a warning. """
        self.log(message, 2)

    def error(self, message):
        """ Log an error. """
        self.log(message, 3)

    def cb_sep_rclick(self, event):
        """ Called when the toolbar separator is right clicked. 
        
        Default behaviour pops up the toolbar menu. Override this method to
        change this behaviour.
        """
        self.toolbar_popup.popup(event.time)

    def cb_sep_dclick(self, event):
        """ Called when the horizontal separator bar is double clicked. 
        
        Override this method to add desired bahaviour
        """
        pass

    def cb_alternative(self):
        """ The alternative function called for non detachable plugins. """
        pass
    
    def cb_toggledetatch(self, *a):
        """ Called back when the detach button is clicked. """
        # Check whether the detach button is active or not.
        if self.dtbut.get_active():
            # Detach detachable plugins, or call the alternative callback.
            if self.DETACHABLE:
                self.detatch()
            else:
                self.cb_alternative()
                # Ensure the toggle button behaves normally.
                self.dtbut.set_active(False)
        else:
            # Reattach detached plugins.
            if self.DETACHABLE:
                self.attach()

    def evt_init(self):
        """ Called on initializing the plugin.
        
        You are advised to call this method at least if overriding."""
        # Hide the transient windows
        self.msgbox.hide()
        self.qstbox.hide()

    def evt_started(self, serverlist):
        """ Called after creation. """
        pass

    def evt_die(self):
        """ Called before shut-down. """
        pass

    def evt_reset(self):
        """ Called when main configuration has been changed. """
        pass

    def evt_shortcuts(self):
        """ Called for shortcuts window to be shown. """
        pass

    def evt_shortcutschanged(self):
        """ Called when shortcuts have been changed. """
        pass

    def evt_newterm(self, command, args, **kw):
        """ Called to open a command in a new terminal. """
        pass

    def evt_log(self, message, details, level=0):
        """ Called to log a mesage. """
        pass

    def evt_connectserver(self, name):
        """ Called to connect to a server. """
        pass
    
    def evt_serverchange(self, servername):
        """ Called when the server is changed """
        pass

    def evt_badserver(self, name):
        """ Called after attempting to connect to a bad server. """
        pass

    def evt_bufferlist(self, bufferlist):
        """ Called when a new buffer list is received. """
        pass
        
    def evt_bufferchange(self, i, name):
        """ Called when the buffer number has changed. """
        pass

    def evt_bufferunload(self, *a):
        """ Called when a buffer is unloaded """
        pass

    def evt_bufferexecute(self):
        """ Called to execute the contents of a buffer. """
        pass

    def evt_breakpointset(self, line, fn=None):
        """ Called to set a breakpoint. """
        pass

    def evt_breakpointclear(self, line, fn=None):
        """ Called to clear a breakpoint. """
        pass

    def evt_projectexecute(self, arg):
        """ Called to execute the project. """  
        pass

    def evt_pydoc(self, text):
        """ Called to perform a pydoc lookup. """
        pass

