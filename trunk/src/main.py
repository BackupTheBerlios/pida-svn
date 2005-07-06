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

# System imports
import os
import sys
import logging
import optparse

# Gtk
import gtk
import gobject

# Pida
import gtkextra
import configuration.options as options
import configuration.config as config
import configuration.registry as registry
# Version String
import pida.__init__
__version__ = pida.__init__.__version__

# Available plugins, could be automatically generated
PLUGINS = ['project', 'python_browser', 'python_debugger', 'python_profiler',
'gazpacho']

# Convenience method to ease importing plugin modules by name.
def create_plugin(name, cb):
    """ Find a named plugin and instantiate it. """
    # import the module
    # The last arg [True] just needs to be non-empty
    try:
        mod = __import__('pida.plugins.%s.plugin' % name, {}, {}, [True])
        try:
            inst = mod.Plugin(cb)
        except Exception, e:
            logging.warn('Plugin "%s" failed to instantiate: %s' % (name, e))
            inst = None
    except ImportError, e:
        logging.warn('Plugin "%s" failed to import with: %s' % (name, e))
        inst = None

    return inst


class DummyOpts(object):
    """
    A dummy object to make the transition to the new registry
    """
    def __init__(self, cb):
        self.cb = cb

    def get(self, groupname, optname):
        group = getattr(self.cb.registry, groupname)
        option = getattr(group, optname)
        return option.value()

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
        #self.opts = options.Opts()
        self.opts = DummyOpts(self)
        # Icons shared
        self.server = None
        self.startup()
        # Shortcuts
        # Communication window
        #self.cw = Window(self)
        # Ensure that there is no initial server set.
        # start
        self.action_log('Pida', 'started', 0)
        # fire the init event, telling plugins to initialize
        #self.cw.fetch_serverlist()
        #self.cw.feed_serverlist()
        #self.evt('init')
        # fire the started event with the initial server list
        #self.evt('started', None)

    def startup(self):
        self.optparser = optparse.OptionParser()
        self.registry = registry.Registry(os.path.expanduser('~/.pida/pida.conf'))
       
        options.configure(self.registry)

        # The editor 
        self.set_editor('vim')

        # now the plugins
        shell_plug = self.add_plugin('terminal')
        buffer_plug = self.add_plugin('buffer')
        
      
        opt_plugs = []
        for plugname in PLUGINS:
            plugin = self.add_plugin(plugname)
            if plugin and plugin.VISIBLE:
                opt_plugs.append(plugin)
        
        self.shortcuts = self.add_plugin('shortcuts')

        self.evt('init')
       
       
        self.registry.prime_optparser(self.optparser)
        self.optparser.parse_args()
        self.registry.load()
        self.registry.save()
      

        logging.getLogger().setLevel(self.registry.log.level.value())

        self.shortcuts.load()
      
        self.icons = gtkextra.Icons(self)
        # Tooltips shared
        self.tips = gtk.Tooltips()
        self.tips.enable()

        self.mainwindow = MainWindow(self)

        self.evt('populate')
        self.mainwindow.set_plugins(self.editor, buffer_plug, shell_plug, opt_plugs)
        self.mainwindow.show_all()

        self.evt('shown')
        self.evt('started')
        self.evt('reset')
        
    def reset(self):
        logging.getLogger().setLevel(self.registry.log.level.value())

    def add_plugin(self, name):
        """
        Create and return the plugin
        """
        plugin = create_plugin(name, self)
        if plugin:
            plugin.configure(self.registry)
            self.plugins.append(plugin)
        return plugin

    def set_editor(self, name):
        """
        Set the editor plugin
        """
        self.editor = self.add_plugin(name)
        return self.editor

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

    def action_log(self, message, details, level=10):
        """ called to make log entry """
        # Call the log event, the log itself will respond.
        # self.evt('log', message, details, level)
        logging.getLogger().log(level, '%s: %s' % (message, details))

    def action_close(self):
        """ Quit Pida. """
        # Tell plugins to die
        self.evt('die')
        # Fin
        gtk.main_quit()

    def action_newterminal(self, command, args, **kw):
        """Open a new terminal, by issuing an event"""
        self.action_log('action', 'newterminal', 0)
        # Fire the newterm event, the terminal plugin will respond.
        self.evt('newterm', command, args, **kw)

    def edit(self, name, *args, **kw):
        funcname = 'edit_%s' % name
        if hasattr(self.editor, funcname):
            try:
                getattr(self.editor, funcname)(*args, **kw)
            except Exception, e:
                logging.warn('error passing event "%s" to editor %s' % (name, e))
        else:
            logging.warn('Edtor does not support %s.' % name)


    def evt(self, name, *args, **kw):
        """Callback for events from vim client, propogates them to plugins"""
        # log all events except for log events
        if name != 'log':
            self.action_log('event', name)
        if name == 'reset':
            self.reset()
        # pass the event to every plugin
        eventname = 'evt_%s' % name
        for plugin in self.plugins:
            # call the instance method, or an empty lambda
            eventfunc = getattr(plugin, eventname, None)
            if eventfunc:
                try:
                    eventfunc(*args, **kw)
                except Exception, e:
                    logging.warn('error passing event "%s" to %s %s' % (name,
                                 plugin, e))

    def attr(self, name, callbackfunc, *args, **kw):
        attrname = 'attr_%s' % name
        for plugin in self.plugins:
            attrfunc = getattr(plugin, attrname, None)
            if attrfunc:
                result = attrfunc(*args, **kw)
                callbackfunc(result)
    
# The main application window.
class MainWindow(gtk.Window):
    """ the main window """
    def __init__(self, cb):
        self.cb =cb
        gtk.Window.__init__(self)
        # Set the window title.
        caption = 'PIDA %s' % __version__
        self.set_title(caption)
        # Connect the destroy event.
        self.connect('destroy', self.cb_quit)
        # Connect the keypress event.
        self.connect('key_press_event', self.cb_key_press)
        # The outer pane

    def set_plugins(self, server_plug, buffer_plug, shell_plug, opt_plugs):
        p0 = gtk.HPaned()
        
        self.cb.embedwindow = gtk.VBox()
        self.cb.embedslider = p0
        p0.pack1(self.cb.embedwindow, True, True)
        
        p1 = gtk.VPaned()

        if self.cb.registry.vim.embedded_mode.value():
            self.resize(1000, 768)
            self.add(p0)
            p0.pack2(p1, True, True)
            p0.set_position(600)
        else:
            self.resize(400, 768)
            self.add(p1)
        # Pane for standard and optional plugins
        p2 = None
        if self.cb.registry.layout.vertical_split.value():
            p2 = gtk.VPaned()
        else:
            p2 = gtk.HPaned()
        p1.pack1(p2, True, True)
        p1.pack2(shell_plug.win, True, True)
        lbox = gtk.VBox()
        lbox.set_size_request(200, -1)
        p2.pack1(lbox, True, True)
        lbox.pack_start(server_plug.win, expand=False)
        lbox.pack_start(buffer_plug.win)
        # The optional plugin  area
        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(True)
        self.notebook.set_size_request(200, -1)
        p2.pack2(self.notebook, True, True)
        # Populate with the configured plugins
        for plugin in opt_plugs:
            self.add_opt_plugin(plugin)
        # Show the window as late as possible.

        
    
    def add_opt_plugin(self, plugin):
        """
        Add a plugin to the optional plugin notebook.
        
        @param plugin: An instance of the plugin.
        @type plugin: pida.plugin.Plugin
        """
        # create a label with a tooltip/EventBox
        eb = gtk.EventBox()
        tlab = gtk.HBox()
        eb.add(tlab)
        self.cb.tips.set_tip(eb, plugin.NAME)
        im = self.cb.icons.get_image(plugin.ICON)
        tlab.pack_start(im, expand=False)
        #label = gtk.Label('%s' % plugin.NAME[:2])
        #tlab.pack_start(label, expand=False, padding=2)
        tlab.show_all()
        # create a new notebook page
        self.notebook.append_page(plugin.win, tab_label=eb)
        self.notebook.show_all()
        # Remove the toolbar label present by default on plugins
        plugin.ctlbar.remove(plugin.label)

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
        # self.save_geometry()
        self.cb.action_close()
   

def main(argv):
    a = Application()
    gtk.main()

if __name__ == '__main__':
    main(sys.argv)



