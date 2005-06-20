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
    """ The base plugin class. 
    
        This class is to be overriden for any object that wishes to have a
        reference to the main Application object, or wishes to receive events
        generated by the main Application object.
    """
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
        """ 
        Constructor
        
        @param cb: An instance of the main application class.
        @type cb: C{pida.main.Application}

        @note: It is recommended that to add additional widgets to the plugin,
        that the populate_widgets method is overriden instead of this
        constructor.
        """
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
        """
        Called after the constructor to populate the plugin.
        
        Override this method and add the desired widgets to the plugin.
        """
        pass

    def connect_widgets(self):
        """ 
        Called after widget population to connect signals.
        """
        pass

    def add(self, widget, *args, **kwargs):
        """
        Add a widget to the plugin.
        
        @param widget: The widget to add.
        @type widget: L{gtk.Widget}
        
        @param *args: Additional arguments to pass the pack_start method.
        @param **kwargs: Additional kwargs to pass the pack_start method.
        
        @note: use C{expand=False} in kwargs, to prevent widget expanding.
        """
        self.frame.pack_start(widget, *args, **kwargs)

    def add_button(self, stock, callback, tooltip='None Set!', cbargs=[]):
        """
        Add a button to the plugin toolbar and toolbar menu.
        
        @param stock: The icon name.
        @type stock: string
        
        @param callback: The function to call back on button activation
        @type callback: function

        @param tooltip: The tooltip to display for the button.
        @type: tooltip: string

        @param cbargs: A list of arguments to pass the callback function.
        @type cbargs: list

        @return: The newly created button.
        @rtype: L{gtk.ToolButton}
        """
        self.toolbar_popup.add_item(stock, tooltip, callback, cbargs)
        return self.cusbar.add_button(stock, callback, tooltip, cbargs)
    
    def add_separator(self):
        """
        Add a separator to the toolbar and toolbar menu.
        """
        self.toolbar_popup.add_separator()
        self.cusbar.add_separator()
        
    def message(self, message):
        """ 
        Give the user a message in a transient window.
        
        @param message: The text of the message to give the user.
        @type message: C{str}
        """
        self.msgbox.message(message)

    def question(self, message, callback):
        """
        Ask the user a question in a transient window.
        
        The question is popped up to the user inside the plugin, and the
        callback method is called on successful submission with the answer as
        argument.

        @param message: The prompt to display.
        @type message: string

        @param callback: The function to callback on submission.
        @type callback: function

        @note: the signature of the callback function will be:

            C{def callback_function(answer):} for functions, and

            C{def callback_function(self, answer):} for class methods.
        """
        self.qstbox.question(message, callback)

    def attach(self, *a):
        """
        Reparent the plugin in the original parent.
        """
        self.win.reparent(self.oldparent)
        self.dwin.destroy()
    
    def detatch(self):
        """
        Reparent the plugin in a top-level window.
        """
        self.oldparent = self.win.get_parent()
        self.dwin = gtkextra.Winparent(self.cb, self)

    def log(self, message, level):
        """
        Log a message.
        
        @param message: The message to be logged.
        @type message: string

        @param level: The log level.
        @type level: int
        """
        # Add plugin name to message.
        text = '%s: %s' % (self.NAME, message)
        # Call the main log event.
        self.cb.action_log(self.NAME, message, level)

    def debug(self, message):
        """
        Log a debug message. 
        
        @param message: The message to be logged.
        @type message: string
        """

        self.log(message, 0)

    def info(self, message):
        """
        Log an info message.

        @param message: The message to be logged.
        @type message: string
        """
        self.log(message, 1)

    def warn(self, message):
        """
        Log a warning. 
        
        @param message: The message to be logged.
        @type message: string
        """
        self.log(message, 2)

    def error(self, message):
        """
        Log an error. 
        
        @param message: The message to be logged.
        @type message: string
        """
        self.log(message, 3)

    def cb_sep_rclick(self, event):
        """
        Called when the toolbar separator is right clicked. 
        
        Default behaviour pops up the toolbar menu. Override this method to
        change this behaviour.

        @param event: The gdk event firing the callback.
        @type event: gtk.gdk.Event
        """
        self.toolbar_popup.popup(event.time)

    def cb_sep_dclick(self, event):
        """
        Called when the horizontal separator bar is double clicked. 
        
        Override this method to add desired bahaviour

        @param event: The gdk event firing the callback.
        @type event: gtk.gdk.Event
        """
        pass

    def cb_alternative(self):
        """
        The alternative function called for non detachable plugins.
        """
        pass
    
    def cb_toggledetatch(self, *a):
        """
        Called back when the detach button is clicked.

        Detach the plugin for a detachable plugin, or call the alternative
        callback for undetachable plugins.
        """
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
        """
        Event: called on initializing the plugin.
        
        You are advised to call this method at least if overriding.
        """
        # Hide the transient windows
        self.msgbox.hide()
        self.qstbox.hide()

    def evt_started(self, serverlist):
        """
        Event: called on starting.
        
        @param serverlist: A list of servers registered with the X root
            window.
        @type serverlist: C{list} of C{(name, X-window ID)} pairs
        """
        pass

    def evt_die(self):
        """ 
        Event: Called before shut-down.
        """
        pass

    def evt_reset(self):
        """ 
        Event: called when main configuration has been changed.
        """
        pass

    def evt_shortcuts(self):
        """
        Event: called for shortcuts window to be shown.
        """
        pass

    def evt_shortcutschanged(self):
        """
        Event: Called when shortcuts have been changed.
        """
        pass

    def evt_newterm(self, command, args, **kwargs):
        """
        Event: called to open a command in a new terminal.
        
        @param command: The path to the command to be executed.
        @type command: string

        @param args: The argument list to pass the command (this usually
            starts with the command name as the first argument)
        @type args: list

        @param kwargs: a list of additional keyword args to pass the terminal.
            See the VTE reference manual for details.
        """
        pass

    def evt_log(self, title, message, level=0):
        """
        Event: called to log a mesage.
        
        @param title: The title of the message.
        @type title: string
        
        @param message: The message.
        @type message: string

        @param level: The level to be logged.
        @type level: int
        """
        pass

    def evt_connectserver(self, servername):
        """
        Event: called to connect to a server.
        
        @param servername: The server to connect to.
        @type servername: string
        """
        pass
    
    def evt_serverchange(self, servername):
        """
        Event: called when the server is changed

        @param servername: The server connected to.
        @type servername: string
        """
        pass

    def evt_badserver(self, servername):
        """
        Event: called after attempting to connect to a bad server.

        @param servername: The bad server name.
        @type servername: string
        """
        pass

    def evt_bufferlist(self, bufferlist):
        """
        Event: called when a new buffer list is received.
        
        @param bufferlist: A list of loaded buffers.
        @type bufferlist a C{list} of C{(number, name)} pairs
        """
        pass
        
    def evt_bufferchange(self, buffernumber, buffername):
        """
        Event: called when the buffer number has changed.

        @param buffernumber: The number of the buffer changed to.
        @type buffernumber: string

        @param buffername: The path of the buffer changed to on disk.
        @type buffername: string
        """
        pass

    def evt_bufferunload(self, *a):
        """
        Event: called when a buffer is unloaded.
        """
        pass

    def evt_bufferexecute(self):
        """
        Called to execute the contents of a buffer.
        """
        pass

    def evt_breakpointset(self, line, filename=None):
        """
        Called to set a breakpoint.

        If no filename is passed, it is assumed that the current filename is
        specified.

        @param line: The line number to place the brakpoint.
        @type line: int or string

        @param filename: The filename to place the breakpoint.
        @type filename: string
        """
        pass

    def evt_breakpointclear(self, line, filename=None):
        """
        Event: called to clear a breakpoint.
        
        If no filename is passed, it is assumed that the current filename is
        specified.

        @param line: The line number to clear the brakpoint.
        @type line: int or string

        @param filename: The filename to clear the breakpoint.
        @type filename: string
        """
        pass

    def evt_projectexecute(self, *a):
        """
        Event: called to execute the project.
        """  
        pass

    def evt_pydoc(self, text):
        """
        Called to perform a pydoc lookup.

        @param text: The text to lookup in pydoc.
        @type text: string
        """
        pass

