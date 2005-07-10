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

# The main application window.
class MainWindow(gtk.Window):
    """ the main window """
    def __init__(self, cb):
        self.cb =cb
        gtk.Window.__init__(self)
        # Set the window title.
        caption = 'PIDA' # %s' % __version__
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

        if (self.cb.registry.layout.embedded_mode.value() and \
            self.cb.editor.NAME == 'Vim') or self.cb.editor.NAME == 'Culebra':
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
        self.opt_plugins = opt_plugs
        self.opt_windows = {}
        for plug in opt_plugs:
            self.add_opt_plugin(plug)
        self.add_pages(self.cb.boss.get_pluginnames('None'))
        # Show the window as late as possible.

        
    def add_pages(self, pluginnames):
        for plugin in self.opt_plugins:
            pluginname = plugin.NAME
            pagenum = self.notebook.page_num(plugin.win)
            if pluginname in pluginnames:
                if pagenum < 0:
                    self.display_plugin(pluginname)
            else:
                if pagenum > -1:
                    self.notebook.remove_page(pagenum)
                
    
    def add_opt_plugin(self, plugin):
        """
        Add a plugin to the optional plugin notebook.
        
        @param plugin: An instance of the plugin.
        @type plugin: pida.plugin.Plugin
        """
        # Remove the toolbar label present by default on plugins
        plugin.ctlbar.remove(plugin.label)
        # create a label with a tooltip/EventBox
        label = gtk.EventBox()
        self.cb.tips.set_tip(label, plugin.NAME)
        im = self.cb.boss.icons.get_image(plugin.ICON)
        im.show()
        label.add(im)
        
        # store the page fand label for later use
        self.opt_windows[plugin.NAME] = (plugin.win, label)


    def display_plugin(self, pluginname):
        if pluginname in self.opt_windows:
            win, label = self.opt_windows[pluginname]
            self.notebook.append_page(win, tab_label=label)


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
   
