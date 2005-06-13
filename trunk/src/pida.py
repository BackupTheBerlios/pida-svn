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
import gdkvim
import plugin
import icons
import options
import config
import pida_server
import pida_buffer
import pida_shell
import pida_shortcuts

# Version String
import __init__
__version__ = __init__.__version__



class App(object):
    '''The application class, a glue for everything'''
    def __init__(self):
        # List of plugins loaded used for event passing
        self.plugins = []
        # Main config options
        self.opts = options.Opts()
        # Icons shared
        self.icons = icons.Icons(self)
        # Tooltips shared
        self.tips = gtk.Tooltips()
        self.tips.enable()
        # Shortcuts
        self.shortcuts = pida_shortcuts.Plugin(self)
        self.plugins.append(self.shortcuts)
        # Communication window
        self.cw = Window(self)
        self.cw.connect('destroy', self.cb_quit)
        #
        self.server = None
        # start
        self.action_start()

    def action_reset(self):
        ''' called when the config has changed '''
        self.evt('reset')

    def action_resetshortcuts(self):
        ''' Called when the shortcuts have been changed ''' 
        self.evt('shortcutschanged')

    def action_showconfig(self):
        ''' called to show the config editor '''
        self.configeditor = config.ConfigEditor(self)
        self.configeditor.show()

    def action_showshortcuts(self):
        ''' called to show the shortcut editor '''
        self.shortcuts = pida_shortcuts.Plugin(self)
        self.shortcuts.evt_init()
        self.shortcuts.show()

    def action_log(self, message, details, level=0):
        ''' called to make log entry '''
        self.evt('log', message, details, level)

    # might get rid of this
    def action_start(self):
        ''' called when pida started '''
        self.action_log('action', 'start', 0)
        self.evt('init')
        self.evt('started', self.cw.serverlist())

    def action_close(self):
        ''' Quit Pida. '''
        # Tell plugins to die
        self.evt('die')
        # Fin
        gtk.main_quit()

    def action_connectserver(self, server):
        ''' Connect to the named server. '''
        self.action_log('action', 'connectserver', 0)
        self.server = server
        #vs = self.opts.get('files', 'script_vim')
        #self.cw.send_ex(self.server, 'so %s' % vs)
        # Send the server change event
        self.evt('connectserver', server)

    def action_closebuffer(self):
        self.action_log('action', 'closebuffer', 0)
        self.cw.close_buffer(self.server)

    def action_gotoline(self, ln):
        self.action_log('action', 'gotoline', 0)
        self.cw.change_cursor(self.server, 1, ln)
        self.action_foreground()

    def action_getbufferlist(self):
        ''' Get the buffer list. '''
        self.action_log('action', 'getbufferlist', 0)
        self.cw.get_bufferlist(self.server)

    def action_getcurrentbuffer(self):
        ''' Ask Vim to return the current buffer number. '''
        self.cw.get_current_buffer(self.server)

    def action_changebuffer(self, nr):
        '''Change buffer in the active vim'''
        self.action_log('action', 'changebuffer', 0)
        self.cw.change_buffer(self.server, nr)
        self.action_foreground()
   
    def action_foreground(self):
        ''' Put vim into the foreground '''
        if int(self.opts.get('vim', 'foreground_jump')):
            self.cw.foreground(self.server)
            #if self.opts.get('vim', 'mode_embedded') == '1':
            #    self.embedwindow.get_children()[0].grab_focus()
 
    def action_openfile(self, fn):
        '''open a new file in the connected vim'''
        self.action_log('action', 'openfile', 0)
        self.cw.open_file(self.server, fn)

    def action_preview(self, fn):
        self.cw.preview_file(self.server, fn)

    def action_newterminal(self, command, args, **kw):
        '''Open a new terminal, by issuing an event'''
        self.action_log('action', 'newterminal', 0)
        self.evt('newterm', command, args, **kw)

    def send_ex(self, ex):
        ''' Send a normal mode command. '''
        if self.server:
            self.cw.send_ex(self.server, ex)

    def get_serverlist(self):
        '''Get the list of servers'''
        return self.cw.serverlist()

    def evt(self, name, *value, **kw):
        '''Callback for events from vim client, propogates them to plugins'''
        if name != 'log':
            self.action_log('event', name)
        for plugin in self.plugins:
            getattr(plugin, 'evt_%s' % name, lambda *a, **k: None)(*value, **kw)

    def cb_quit(self, *a):
        '''Callback for user closing the main window'''
        self.action_close()

class Window(gdkvim.VimWindow):
    ''' the main window '''
    def __init__(self, cb):
        gdkvim.VimWindow.__init__(self, cb)
        self.set_size_request(20,200)
        self.resize(400,800)
        caption = 'PIDA %s' % __version__
        self.set_title(caption)
        self.connect('key_press_event', self.cb_key_press)

        self.bh = BarHolder(self.cb)
        self.add(self.bh)
        self.show()

    def cb_key_press(self, widget, event):
        #keyname = gtk.gdk.keyval_name(event.keyval)
        #print "Key %s (%d) was pressed" % (keyname, event.keyval)
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.keyval == 97:
                print '<C-a>'
                return True
            elif event.keyval == 115:
                print '<C-a>'
                return True
        return False
# Will be moved
class BarNotebook(gtk.EventBox):
    def __init__(self, cb):
        self.cb = cb
        gtk.EventBox.__init__(self)
        self.show()
        self.nb = gtk.Notebook()
        self.add(self.nb)
        self.nb.set_show_border(True)
        self.nb.show()

    def add_plugin(self, plugintype):
        plugin = plugintype(self.cb)
        self.cb.plugins.append(plugin)
        eb = gtk.EventBox()
        tlab = gtk.HBox()
        eb.add(tlab)
        self.cb.tips.set_tip(eb, plugin.NAME)
        im = self.cb.icons.get_image(plugin.ICON)
        tlab.pack_start(im, expand=False)
        label = gtk.Label('%s' % plugin.NAME[:2])
        tlab.pack_start(label, expand=False, padding=2)
        tlab.show_all()
        self.nb.append_page(plugin.win, tab_label=eb)
        self.nb.show_all()
        plugin.ctlbar.remove(plugin.label)
# will be moved   
class BarHolder(gtk.HPaned):
    def __init__(self, cb):
        self.cb = cb
        self.cb.barholder = self
        gtk.HPaned.__init__(self)
        self.show()

        self.cb.embedwindow = gtk.VBox()
        self.pack1(self.cb.embedwindow, True, True)
        
        p1 = gtk.VPaned()
        p1.show()
        self.pack2(p1, True, True)

        p2 = gtk.HPaned()
        p2.show()
        p1.pack1(p2, True, True)
        
        p1.set_position(550)
        p2.set_position(200)

        shell_plug = pida_shell.Plugin(self.cb)
        self.cb.plugins.append(shell_plug)
        p1.pack2(shell_plug.win, True, True)

        lbox = gtk.VBox()
        lbox.show()
        p2.pack1(lbox, True, True)

        server_plug = pida_server.Plugin(self.cb)
        lbox.pack_start(server_plug.win, expand=False)
        self.cb.plugins.append(server_plug)

        buffer_plug = pida_buffer.Plugin(self.cb)
        lbox.pack_start(buffer_plug.win)
        self.cb.plugins.append(buffer_plug)

        self.barbook = BarNotebook(self.cb)
        p2.pack2(self.barbook, True, True)
        
        if int(self.cb.opts.get('plugins', 'python_general')):
            import pida_python
            self.barbook.add_plugin(pida_python.Plugin)
        if int(self.cb.opts.get('plugins', 'project')):
            import pida_project
            self.barbook.add_plugin(pida_project.Plugin)
        if int(self.cb.opts.get('plugins', 'python_debugger')):
            import pida_debugger
            self.barbook.add_plugin(pida_debugger.Plugin)
        if self.cb.opts.get('plugins', 'profiler_python') == '1':
            import pida_profiler
            self.barbook.add_plugin(pida_profiler.Plugin)

def main(argv):
    a = App()
    gtk.main()

if __name__ == '__main__':
    main(sys.argv)



