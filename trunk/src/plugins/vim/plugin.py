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
import time
# GTK imports
import gtk
import gobject
# Pida imports
import pida.plugin as plugin
import vimembed
import pida.gtkextra as gtkextra


SHORTCUTS = [('shortcut_execute',
                'Async_event("bufferexecute,")'),
             ('shortcut_project_execute',
                'Async_event("projectexecute,")'),
             ('shortcut_breakpoint_set',
                'Async_event("breakpointset,".line("."))'),
             ('shortcut_breakpoint_clear',
                'Async_event("breakpointclear,".line("."))'),
             ('shortcut_pydoc_yanked',
                '''Async_event("pydoc,".expand('<cword>'))'''),
             ('shortcut_pydoc_cursor',
                'Async_event("pydoc,".@")')]

NMAP_COM = 'nmap %s :call %s<lt>CR>'

UNMAP_COM = 'nun %s'

VIMSCRIPT = ''':silent function! Bufferlist()
let i = 1
    let max = bufnr('$') + 1
    let lis = ""
    while i < max
        if bufexists(i)
            let lis = lis.";".i.":".bufname(i)
        endif
        let i = i + 1
    endwhile
    return lis
endfunction
:silent function! Async_event(e)
    let c = "call server2client('".expand('<client>')."', '".a:e."')"
    try
        exec c
    catch /.*/
        echo c
    endtry
endfunction
:silent augroup pida
:silent au! pida
:silent au pida BufEnter * call Async_event("bufferchange,".bufnr('%').",".bufname('%'))
:silent au pida BufDelete * call Async_event("bufferunload,")
:echo "PIDA connected"
'''

class Plugin(plugin.Plugin):
    NAME = "Server"
    RESIZABLE = False
    DICON = 'configure', 'Configure Pida'

    def populate_widgets(self):
        self.add_button('connect', self.cb_connect,
            'Connect to Vim session')
        self.add_button('editor', self.cb_run,
            'Execute a new Vim session')
        self.add_button('refresh', self.cb_refresh,
            'Refresh server list')
        self.entry = gtk.combo_box_new_text()
        self.add(self.entry, False)
        self.old_shortcuts = []
        self.vim = None
        self.embedname = None
        #gobject.timeout_add(2000, self.cb_refresh)
        self.currentserver = None
        self.oldservers = []
    
    def launch(self):
        vc = 'vim'
        if int(self.cb.opts.get('vim', 'mode_easy')):
            vc = 'evim'
        vimcom = self.cb.opts.get('commands', vc)
        if self.is_embedded():
            if self.vim:
                self.message('Only one embedded Vim allowed.')
            else:
                name = self.generate_embedname()
                self.vim = vimembed.PidaVim(self.cb,
                                            self.cb.embedwindow, vimcom, name)
                self.vim.connect(self.cb_plugged, self.cb_unplugged)
        else:
            os.system('%s --servername pida' % vimcom)

    def refresh(self, serverlist):
        if serverlist != self.oldservers:
            self.oldservers = serverlist
            actiter = self.entry.get_active_iter()
            act = None
            if actiter:
                act = self.entry.get_model().get_value(actiter, 0)
            #self.cb.action_connectserver(name)
            self.entry.get_model().clear()
            for i in serverlist:
                s = i.strip()
                if self.is_embedded():
                    if s == self.embedname:
                        self.entry.append_text(s.strip())
                        if self.currentserver != s:
                            self.cb.action_connectserver(s)
                else:
                    self.entry.append_text(s.strip())
            self.entry.show_all()
            if act:
                for row in self.entry.get_model():
                    if row[0] == act:
                        self.entry.set_active_iter(row.iter)
            else:
                self.entry.set_active(0)

    def load_shortcuts(self):
        if self.old_shortcuts:
            for sc in self.old_shortcuts:
                self.cb.send_ex(UNMAP_COM % sc)
        self.old_shortcuts = []

        l = self.cb.opts.get('vim shortcuts', 'shortcut_leader')
        
        for name, command in SHORTCUTS:
            c = self.cb.opts.get('vim shortcuts', name)
            sc = ''.join([l, c])
            self.old_shortcuts.append(sc)
            self.cb.send_ex(NMAP_COM % (sc, command))


    def generate_embedname(self):
        self.embedname = 'PIDA_EMBED_%s' % time.time()
        return self.embedname

    def is_embedded(self):
        return self.cb.opts.get('vim', 'mode_embedded') == '1'

    def cb_plugged(self):
        #self.cb.embedwindow.set_size_request(600, -1)
        #self.cb.barholder.set_position(200)
        pass

    def cb_unplugged(self):
        #self.cb.embedwindow.set_size_request(0, -1)
        #self.cb.barholder.set_position(0)
        self.vim = None

    def cb_connect(self, *a):
        iter = self.entry.get_active_iter()
        if iter:
            name = self.entry.get_model().get_value(iter, 0)
            self.cb.action_connectserver(name)
   
    def cb_refresh(self, *args):
        self.refresh(self.cb.get_serverlist())
        return True

    def cb_run(self, *args):
        self.launch()

    def cb_alternative(self, *args):
        self.cb.action_showconfig()

    #def evt_die(self):
    #    if self.vim:
    #        self.cb.action_quitvim()
            

    def evt_reset(self):
        self.load_shortcuts()

    def evt_connectserver(self, name):
        self.currentserver = name
        self.load_shortcuts()
        self.cb.send_ex('%s' % VIMSCRIPT)
        self.cb.action_foreground()
        self.cb.evt('serverchange', name)

    def evt_started(self, serverlist):
        if self.is_embedded():
            self.launch()
        elif int(self.cb.opts.get('vim', 'connect_startup')):
            self.cb_connect()

    def evt_serverlist(self, serverlist):
        self.refresh(serverlist)


    #def evt_badserver(self, name):
    #    self.cb_refresh()
    #    self.cb_connect()

    def evt_serverchange(self, name):
        pass
