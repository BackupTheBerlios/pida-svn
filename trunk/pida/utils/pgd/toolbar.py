# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

# Copyright (c) 2006 Ali Afshar

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


from components import PGDSlaveDelegate


class Toolbar(PGDSlaveDelegate):

    def _create_uim(self):
        self.uim = gtk.UIManager()
        self.action_group = gtk.ActionGroup('main')
        self.uim.insert_action_group(self.action_group, 0)
        self.action_group.add_actions([
            ('Step', 'dbgstep', 'Step', '<Ctrl>s',
             'Step the debugger', self.on_step),
            ('Go', gtk.STOCK_MEDIA_PLAY, 'Go', '<Ctrl>g',
             'Continue the debugger until it breaks.', self.on_go),
            ('Return', 'dbgstepout', 'Return', '<Ctrl>r',
            'Return', self.on_return),
            ('Break', gtk.STOCK_MEDIA_PAUSE, 'Break', '<Ctrl>x',
            'Break', self.on_break),
            ('Next', 'dbgnext', 'Next', '<ctrl>n',
             'Next', self.on_next),
             ('Launch', gtk.STOCK_OPEN, 'Launch', '<ctrl>o',
              'Launch a script in the debugger', self.on_launch),
            ('Stop', gtk.STOCK_STOP, 'Stop', '<ctrl>c',
             'Stop the execution', self.on_stop),
            ('Reload', gtk.STOCK_REFRESH, 'Reload', '<ctrl>r',
             'Reload the current file', self.on_reload),
            ('LaunchMenu', None, 'Execute', None, None, None),
            ('ControlMenu', None, 'Control', None, None, None),
            ])
        ui = """
                <menubar>
                    <menu action="LaunchMenu">
                        <menuitem action="Launch" />
                        <menuitem action="Reload" />
                        <menuitem action="Stop" />
                    </menu>
                    <menu action="ControlMenu">
                        <menuitem action="Step" />
                        <menuitem action="Next" />
                        <menuitem action="Return" />
                        <separator />
                        <menuitem action="Go" />
                        <menuitem action="Break" />
                        
                    </menu>
                </menubar>
                <toolbar>
                    <toolitem action="Launch" />
                    <toolitem action="Reload" />
                    <toolitem action="Stop" />
                    <separator />
                    <toolitem action="Go" />
                    <toolitem action="Break" />
                    <separator />
                    <toolitem action="Step" />
                    <toolitem action="Next" />
                    <toolitem action="Return" />
                </toolbar>
             """
        self.uim.add_ui_from_string(ui)
        self.update_state('detached')
        #self.main_window.window.add_accel_group(self.uim.get_accel_group())

    def update_state(self, state):
        smap = {
            'broken': ['Step', 'Next', 'Return', 'Go', 'Stop'],
            'running': ['Stop', 'Break'],
            'detached': ['Launch', 'Reload'],
            'spawning': [],
            }
        for act in self.action_group.list_actions():
            if state in smap:
                if (act.get_name() in smap[state] or
                    act.get_name().endswith('Menu')):
                    act.set_sensitive(True)
                else:
                    act.set_sensitive(False)

    def on_reload(self, action):
        si = self.session_manager._CSessionManager__smi.m_server_info
        if si:
            filename = si.m_filename
            self.session_manager.launch_filename(filename)
        

    def on_step(self, action):
        self.session_manager.request_step()

    def on_go(self, action):
        self.session_manager.request_go()

    def on_return(self, action):
        self.session_manager.request_return()

    def on_break(self, action):
        
        def _break():
            self.session_manager.request_break()
        import threading
        threading.Thread(target=_break).start()

    def on_next(self, action):
        self.session_manager.request_next()

    def on_launch(self, action):
        dlg = gtk.FileChooserDialog(parent=self.main_window.window,
                                    title='Select script to launch',
                                    buttons=(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK,
                                             gtk.RESPONSE_ACCEPT,
                                             ))
        dlg.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        filename = None
        response = dlg.run()
        if response == gtk.RESPONSE_ACCEPT:
            filename = dlg.get_filename()
            self.session_manager.launch_filename(filename)
        dlg.destroy()
 
    def on_stop(self, action):
        def _s():
            self.session_manager.save_breakpoints()
            self.session_manager.stop_debuggee()
        gobject.idle_add(_s)

    def create_toplevel_widget(self):
        self._create_uim()
        vb = gtk.HBox()
        mb = self.uim.get_widget('/menubar')
        vb.pack_start(mb)
        tb = self.uim.get_widget('/toolbar')
        tb.set_style(gtk.TOOLBAR_ICONS)
        tb.set_icon_size(gtk.ICON_SIZE_MENU)
        vb.pack_start(tb)
        return vb

    def attach_slaves(self):
        #self.main_window.attach_slave('toolbar_holder', self)
        self.show_all()


class StatusBar(PGDSlaveDelegate):

    def create_toplevel_widget(self):
        sb = self.add_widget('statusbar', gtk.Statusbar())
        self.running_id = sb.get_context_id('running')
        return sb

    def attach_slaves(self):
        self.main_window.attach_slave('statusbar_holder', self)

    def update_running_status(self, msg):
        self.statusbar.push(self.running_id, 'STATE: %s' % msg)



