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

# System imports
import os
import sys

# Gtk
import gtk
import gobject

# Pida
import gtkextra
import vim.gdkvim as gdkvim
import configuration.options as options
import configuration.config as config

# Version String
import pida.__init__
__version__ = pida.__init__.__version__

# Available plugins, could be automatically generated
PLUGINS = ['project', 'python_browser', 'python_debugger', 'python_profiler']

# Convenience method to ease importing plugin modules by name.
def create_plugin(name, cb):
    """ Find a named plugin and instantiate it. """
    # import the module
    # The last arg [True] just needs to be non-empty
    mod = __import__('pida.plugins.%s.plugin' % name, {}, {}, [True])
    # instantiate the plugin and return it
    return mod.Plugin(cb)

# Instance of this class is passed to every single custom object in Pida,
# as the cb parameter on instantiation.
# It is responsible for performing "actions" on the editor or other compnent
# and also for initiating "events" and propogating them to plugins.
class Application(object):
    """ The application class, a glue for everything """
    def __init__(self):
        # List of plugins loaded used for event passing
        self.plugins = []
        # Main config options
        self.opts = options.Opts()
        # Icons shared
        self.icons = gtkextra.Icons(self)
        # Tooltips shared
        self.tips = gtk.Tooltips()
        self.tips.enable()
        # Shortcuts
        self.shortcuts = create_plugin('shortcuts', self)
        self.plugins.append(self.shortcuts)
        # Communication window
        self.cw = Window(self)
        # Ensure that there is no initial server set.
        self.server = None
        # start
        self.action_log('Pida', 'starting', 0)
        # fire the init event, telling plugins to initialize
        self.evt('init')
        # fire the started event with the initial server list
        self.evt('started', self.cw.serverlist())

    def action_showconfig(self):
        """ called to show the config editor """
        # Create a new configuration editor, and show it.
        self.configeditor = config.ConfigEditor(self)
        self.configeditor.show()

    def action_showshortcuts(self):
        """ called to show the shortcut editor """
        # create a new shortcut editor and show it.
        self.shortcuts = create_plugin('shortcuts', self)
        # is a plugin, so must fire its init event.
        self.shortcuts.evt_init()
        self.shortcuts.show()

    def action_log(self, message, details, level=0):
        """ called to make log entry """
        # Call the log event, the log itself will respond.
        self.evt('log', message, details, level)

    def action_close(self):
        """ Quit Pida. """
        # Tell plugins to die
        self.evt('die')
        # Fin
        gtk.main_quit()

    def action_connectserver(self, servername):
        """ Connect to the named server. """
        self.action_log('action', 'connectserver', 0)
        self.server = servername
        # Send the server change event with the appropriate server
        # The vim plugin (or others) will respond to this event
        self.evt('connectserver', servername)

    def action_closebuffer(self):
        """ Close the current buffer. """
        self.action_log('action', 'closebuffer', 0)
        # Call the method of the vim communication window.
        self.cw.close_buffer(self.server)

    def action_gotoline(self, line):
        self.action_log('action', 'gotoline', 0)
        # Call the method of the vim communication window.
        self.cw.change_cursor(self.server, 1, line)
        # Optionally foreground Vim.
        self.action_foreground()

    def action_getbufferlist(self):
        """ Get the buffer list. """
        self.action_log('action', 'getbufferlist', 0)
        # Call the method of the vim communication window.
        self.cw.get_bufferlist(self.server)

    def action_getcurrentbuffer(self):
        """ Ask Vim to return the current buffer number. """
        # Call the method of the vim communication window.
        self.cw.get_current_buffer(self.server)

    def action_changebuffer(self, number):
        """Change buffer in the active vim"""
        self.action_log('action', 'changebuffer', 0)
        # Call the method of the vim communication window.
        self.cw.change_buffer(self.server, number)
        # Optionally foreground Vim.
        self.action_foreground()
   
    def action_foreground(self):
        """ Put vim into the foreground """
        # Check the configuration option.
        if int(self.opts.get('vim', 'foreground_jump')):
            # Call the method of the vim communication window.
            self.cw.foreground(self.server)
 
    def action_openfile(self, filename):
        """open a new file in the connected vim"""
        self.action_log('action', 'openfile', 0)
        # Call the method of the vim communication window.
        self.cw.open_file(self.server, filename)

    def action_preview(self, filename):
        self.cw.preview_file(self.server, filename)

    def action_newterminal(self, command, args, **kw):
        """Open a new terminal, by issuing an event"""
        self.action_log('action', 'newterminal', 0)
        # Fire the newterm event, the terminal plugin will respond.
        self.evt('newterm', command, args, **kw)

    def send_ex(self, ex):
        """ Send a normal mode command. """
        # Call the method of the vim communication window.
        if self.server:
            self.cw.send_ex(self.server, ex)

    def get_serverlist(self):
        """Get the list of servers"""
        # Call the method of the vim communication window.
        return self.cw.serverlist()

    def evt(self, name, *value, **kw):
        """Callback for events from vim client, propogates them to plugins"""
        # log all events except for log events
        if name != 'log':
            self.action_log('event', name)
        # pass the event to every plugin
        for plugin in self.plugins:
            # call the instance method, or an empty lambda
            getattr(plugin, 'evt_%s' % name,
                    lambda *a, **k: None)(*value, **kw)

# The main application window.
# This is multiply split into 3 Paned sections.
class Window(gdkvim.VimWindow):
    """ the main window """
    def __init__(self, cb):
        gdkvim.VimWindow.__init__(self, cb)
        # Set the minimum size.
        self.set_size_request(20,200)
        # Request a sane initial size.
        self.resize(400,800)
        # Set the window title.
        caption = 'PIDA %s' % __version__
        self.set_title(caption)
        # Connect the destroy event.
        self.connect('destroy', self.cb_quit)
        # Connect the keypress event.
        self.connect('key_press_event', self.cb_key_press)
        # The outer pane
        p0 = gtk.HPaned()
        p0.show()
        self.add(p0)
        # Set these properties for later embedding
        self.cb.barholder = p0
        self.cb.embedwindow = gtk.VBox()
        p0.pack1(self.cb.embedwindow, True, True)
        # The plugin/terminal area
        p1 = gtk.VPaned()
        p1.show()
        p0.pack2(p1, True, True)
        # Pane for standard and optional plugins
        p2 = gtk.HPaned()
        p2.show()
        p1.pack1(p2, True, True)
        # Set sane starting positions
        p1.set_position(550)
        p2.set_position(200)
        # The terminal plugin
        shell_plug = create_plugin('terminal', self.cb)
        self.cb.plugins.append(shell_plug)
        p1.pack2(shell_plug.win, True, True)
        lbox = gtk.VBox()
        lbox.show()
        p2.pack1(lbox, True, True)
        # The vim plugin.
        server_plug = create_plugin('vim', self.cb)
        lbox.pack_start(server_plug.win, expand=False)
        self.cb.plugins.append(server_plug)
        # The buffer explorer plugin.
        buffer_plug = create_plugin('buffer', self.cb)
        lbox.pack_start(buffer_plug.win)
        self.cb.plugins.append(buffer_plug)
        # The optional plugin  area
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(True)
        self.notebook.show()
        p2.pack2(self.notebook, True, True)
        # Populate with the configured plugins
        for plugin in PLUGINS:
            # Check the config value.
            if self.cb.opts.get('plugins', plugin) == '1':
                # Instantiate and add the plugin.
                pi = create_plugin(plugin, self.cb)
                self.add_plugin(pi)
        # Show the window as late as possible.
        self.show()
            
    def cb_key_press(self, widget, event):
        """
        Callback to all key press events.

        This method must return False for the key-press event to be propogated
        to the child widgets.

        @param widget: The widget that received the key-press event.
        @type widget: gtk.Widget

        @param event: The event received.
        @type event: gtk.gdk.Event
        """
        # if <CONTROL> was pressed with the key
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.keyval == 97:
                print '<C-a>'
                # returning True prevents the key event propogating
                return False
            elif event.keyval == 115:
                print '<C-s>'
                return False
        return False
        
    def cb_quit(self, *a):
        """
        Callback for user closing the main window.
        
        This method is called when the main window is destroyed, wither by
        pressing the close button, or by a window manager hint.
        """
        # call the close acition of the application.
        self.cb.action_close()
        
    def add_plugin(self, plugin):
        """
        Add a plugin to the optional plugin notebook.
        
        @param plugin: An instance of the plugin.
        @type plugin: pida.plugin.Plugin
        """
        # add the plugin to the Application's list of plugins
        self.cb.plugins.append(plugin)
        # create a label with a tooltip/EventBox
        eb = gtk.EventBox()
        tlab = gtk.HBox()
        eb.add(tlab)
        self.cb.tips.set_tip(eb, plugin.NAME)
        im = self.cb.icons.get_image(plugin.ICON)
        tlab.pack_start(im, expand=False)
        label = gtk.Label('%s' % plugin.NAME[:2])
        tlab.pack_start(label, expand=False, padding=2)
        tlab.show_all()
        # create a new notebook page
        self.notebook.append_page(plugin.win, tab_label=eb)
        self.notebook.show_all()
        # Remove the toolbar label present by default on plugins
        plugin.ctlbar.remove(plugin.label)

def main(argv):
    a = Application()
    gtk.main()

if __name__ == '__main__':
    main(sys.argv)



