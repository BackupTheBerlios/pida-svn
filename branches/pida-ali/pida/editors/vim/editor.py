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

import pida.core.editor as editor
import vim.gdkvim as gdkvim
import vim.vimembed as vimembed
import pida.core.registry as registry

class Editor(editor.Editor):
    NAME = 'vim' 

    OPTIONS = [('shortcut-leader', 'the lead key for pida shortcuts',
                ',', registry.RegistryItem),
               ('shortcut-execute', 'the lead key for pida shortcuts',
                'x', registry.RegistryItem)]

    def __load_shortcuts(self):
        for mapc in ['n', 'v']:
            if self.__old_shortcuts[mapc].setdefault(self.__srv, []):
                for sc in self.__old_shortcuts[mapc][self.__srv]:
                    self.__cw.send_ex(self.__srv, UNMAP_COM % (mapc, sc))
            self.__old_shortcuts[mapc][self.__srv] = []
            l = self.options.get('shortcut-leader').value()
            for name, command in SHORTCUTS:
                try:
                    c = self.options.get(name).value()
                    sc = ''.join([l, c])
                    self.__old_shortcuts[mapc][self.__srv].append(sc)
                    self.__cw.send_ex(self.__srv, NMAP_COM % (mapc, sc, command))
                except registry.BadRegistryKey:
                    pass

    def reset(self):
        self.boss.command('configmanager', 'reload')
        self.__old_shortcuts = {'n':{}, 'v':{}}
        self.__load_shortcuts()

    def populate(self):
        self.__cw = None
        self.__bufferevents = []

    def launch(self):
        if self.__cw is None:
            self.__cw = gdkvim.VimWindow(self)
            self.__srv = 'PIDA2VIM'
            self.__view = vimembed.PidaVim('gvim', [self.__srv])
        self.boss.command("editor", "add-page", contentview=self.__view)
        self.__view.run()

    def new_serverlist(self, serverlist):
        if 'PIDA2VIM' in serverlist:
            self.__cw.send_ex(self.__srv, '%s' % VIMSCRIPT)
            self.manager.emit_event('started')
            self.reset()

    def open_file(self, filename):
        self.__cw.open_file(self.__srv, filename)
        self.__view.raise_tab()

    def open_file_line(self, filename, linenumber):
        self.open_file(filename)
        self.__bufferevents.append([self.goto_line, (linenumber, )])

    def goto_line(self, linenumber):
        self.__cw.change_cursor(self.__srv, 1, linenumber)

    def vim_bufferchange(self, index, filename):
        print 'bufferchange'
        for fcall, args in self.__bufferevents:
            fcall(*args)
        self.__bufferevents = []
        self.manager.emit_event('file-opened', filename=filename)
            

    def vim_bufferunload(self, *args):
        self.manager.emit_event('current-file-closed')

    def vim_filesave(self, *args):
        self.boss.command('buffer-manager', 'reset-current-buffer')

    def __get_view(self):
        return self.__view
    view = property(__get_view)



SHORTCUTS = [('shortcut-execute',
                'Async_event("bufferexecute,")'),
             ('shortcut_project_execute',
                'Async_event("projectexecute,")'),
             ('shortcut_breakpoint_set',
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
:silent au pida BufDelete * call Async_event("bufferunload,")
:silent au pida VimLeave * call Async_event("vimshutdown,")
:silent au pida BufWritePost * call Async_event("filesave,")
:silent au pida FileType * call Async_event("filetype,".bufnr('%').",".expand('<amatch>'))
:echo "PIDA connected"
'''

