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

class Editor(editor.Editor):
    NAME = 'vim' 

    def populate(self):
        self.__cw = gdkvim.VimWindow(self)
        self.__srv = 'PIDA2VIM'
        self.__view = vimembed.PidaVim('vim', self.__srv)

    def launch(self):
        self.__view.run()

    def new_serverlist(self, serverlist):
        if 'PIDA2VIM' in serverlist:
            self.__cw.send_ex(self.__srv, '%s' % VIMSCRIPT)
            self.manager.emit_event('started')

    def open_file(self, filename):
        self.__cw.open_file(self.__srv, filename)

    def vim_bufferchange(self, index, filename):
        self.manager.emit_event('file-opened', filename=filename)
        print filename

    def vim_bufferunload(self, *args):
        self.manager.emit_event('current-file-closed')

    def __get_view(self):
        return self.__view
    view = property(__get_view)



SHORTCUTS = [('shortcut_execute',
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

