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

import pida.core.service as service
defs = service.definitions
types = service.types

import pida.utils.vim.vimcom as vimcom
import pida.utils.vim.vimembed as vimembed

class vim_editor(service.service):

    single_view_type = vimembed.vim_embed
    single_view_book = 'edit'

    def init(self):
        self.__files = []
        self.__old_shortcuts = {'n':{}, 'v':{}}
        self.__srv = None
        self.__currentfile = None

    def cmd_start(self):
        self.__cw = vimcom.communication_window(self)
        self.create_single_view()
        self.single_view.run()

    def cmd_revert(self):
        self.__cw.revert(self.__srv)

    def cmd_close(self, filename):
        if filename == self.__currentfile:
            self.__cw.close_current_buffer(self.__srv)

    def cmd_edit(self, filename):
        """Open and edit."""
        if filename != self.__currentfile:
            if filename in self.__files:
                self.__cw.change_buffer(self.__srv, filename)
            else:
                self.__cw.open_file(self.__srv, filename)
                self.__files.append(filename)
            self.__currentfile = filename
        self.single_view.raise_page()
        self.single_view.long_title = filename

    def cmd_undo(self):
        self.__cw.undo(self.__srv)

    def cmd_redo(self):
        self.__cw.redo(self.__srv)

    def cmd_cut(self):
        self.__cw.cut(self.__srv)

    def cmd_copy(self):
        self.__cw.copy(self.__srv)

    def cmd_paste(self):
        self.__cw.paste(self.__srv)

    def cmd_save(self):
        self.__cw.save(self.__srv)

    def cmd_goto_line(self, linenumber):
        self.__cw.goto_line(self.__srv, linenumber)

    def has_started(self):
        return self.__srv is not None
    started = property(has_started)

    def vim_new_serverlist(self, serverlist):
        if self.single_view.servername in serverlist and not self.started:
            self.__srv = self.single_view.servername
            self.__cw.send_ex(self.__srv, '%s' % VIMSCRIPT)
            #gobject.timeout_add(3000, self.reset)
            self.reset()
            self.__files = []
            self.get_service('editormanager').events.emit('started')

    def confirm_single_view_controlbar_clicked_close(self, view):
        self.__cw.close_current_buffer(self.__srv)
        return False

    # move to the vimcom library



    def __load_shortcuts(self):
        for mapc in ['n']:
            if self.__old_shortcuts[mapc].setdefault(self.__srv, []):
                for sc in self.__old_shortcuts[mapc][self.__srv]:
                    self.__cw.send_ex(self.__srv, UNMAP_COM % (mapc, sc))
            self.__old_shortcuts[mapc][self.__srv] = []
            #l = self.options.get('shortcut-leader').value
            globalkpsopts = self.boss.option_group('keyboardshortcuts')
            globalkps = []
            for opt in globalkpsopts:
                vals = opt.value().split()
                if len(vals) == 2:
                    mod, k = vals
                v = '<lt>%s-%s>' % (mod, k)
                globalkps.append((v, '''Async_event("globalkp,%s")''' %
                                  opt.value().replace('\\', '\\\\')))
            def load():
                for c, command in globalkps:
                    try:
                        #c = self.options.get(name).value()
                        sc = ''.join([l, c])
                        self.__old_shortcuts[mapc][self.__srv].append(sc)
                        self.__cw.send_ex(self.__srv, NMAP_COM % (mapc, c, command))
                    except registry.BadRegistryKey:
                        pass
            gobject.timeout_add(200, load)

    def reset(self):
        if self.started:
            pass
            #self.__load_shortcuts()

    def open_file_line(self, filename, linenumber):
        if self.__currentfile != filename:
            self.open_file(filename)
            self.__bufferevents.append([self.goto_line, (linenumber, )])
        else:
            self.goto_line(linenumber)

    def goto_line(self, linenumber):
        self.__cw.change_cursor(self.__srv, 1, linenumber)

    def vim_bufferchange(self, index, filename):
        self.__currentfile = filename
        #for fcall, args in self.__bufferevents:
        #    fcall(*args)
        #self.__bufferevents = []
        #self.manager.emit_event('file-opened', filename=filename)
        self.boss.call_command('buffermanager', 'open_file', filename=filename)

    def vim_bufferunload(self, filename, *args):
        if filename != '':
            # unloaded an empty new file
            print self.__files
            if filename in self.__files:
                self.__files.remove(filename)
                self.boss.call_command('buffermanager', 'file_closed',
                                        filename=filename)
            else:
                self.log.info('vim unloaded an unknown file %s', filename)

    def vim_filesave(self, *args):
        self.boss.command('buffer-manager', 'reset-current-buffer')

    def vim_globalkp(self, name):
        self.boss.command('keyboardshortcuts', 'keypress-by-name',
                           kpname=name)



SHORTCUTS = [('shortcut-execute',
                'Async_event("bufferexecute,")'),
             ('shortcut-project-execute',
                'Async_event("projectexecute,")')]
foo=        [('shortcut_breakpoint_set',
                'Async_event("breakpointset,".line("."))'),
             ('shortcut_breakpoint_clear',
                'Async_event("breakpointclear,".line("."))'),
             ('shortcut_doc_yanked',
                '''Async_event("doc,".expand('<cword>'))'''),
             ('shortcut_doc_cursor',
                'Async_event("doc,".@")'),
             ('shortcut_pastebin_yanked',
                '''Async_event("pastebin,".@")'''),
             ('shortcut_switch_focus',
                'Async_event("switchfocus,")')]

NMAP_COM = '%smap %s :call %s<lt>CR>'

UNMAP_COM = '%sun %s'

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
:silent function! Yank_visual()
    y
    return @"
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
:silent au pida BufDelete * call Async_event("bufferunload,".expand('<amatch>'))
:silent au pida VimLeave * call Async_event("vimshutdown,")
:silent au pida VimEnter * call Async_event("started,")
:silent au pida BufWritePost * call Async_event("filesave,")
:silent au pida FileType * call Async_event("filetype,".bufnr('%').",".expand('<amatch>'))
:echo "PIDA connected"
'''

Service = vim_editor
    

