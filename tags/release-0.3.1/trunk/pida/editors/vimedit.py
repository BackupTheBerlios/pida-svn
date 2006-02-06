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


# pida core import(s)
import pida.core.service as service

# pida utils import(s)
import pida.utils.vim.vimcom as vimcom
import pida.utils.vim.vimembed as vimembed
import pida.utils.vim.vimeditor as vimeditor

defs = service.definitions
types = service.types


class vim_embedded_editor(vimeditor.vim_editor, service.service):

    display_name = 'Embedded Vim'

    single_view_type = vimembed.vim_embed
    single_view_book = 'edit'

    def init(self):
        self.__srv = None
        vimeditor.vim_editor.init(self)

    class vim_command(defs.optiongroup):
        """Vim command options."""
        class use_cream(defs.option):
            rtype = types.boolean
            default = False

    class vim_events(defs.optiongroup):
        """How PIDA will react to events from Vim."""
        class shutdown_with_vim(defs.option):
            rtype = types.boolean
            default = False

    def get_server(self):
        """Return our only server."""
        return self.__srv
    server = property(get_server)

    def start(self):
        self.create_single_view()
        if self.opt('vim_command', 'use_cream'):
            command = 'cream'
        else:
            command = 'gvim'
        self.single_view.run(command)

    def vim_new_serverlist(self, serverlist):
        if (self.single_view is not None and
            self.single_view.servername in serverlist and
            not self.started):
            self.__srv = self.single_view.servername
            self.vim_window.init_server(self.server)
            self.reset()
            self.__files = {}
            self.get_service('editormanager').events.emit('started')

    def after_shutdown(self, server):
        if self.opt('vim_events', 'shutdown_with_vim'):
            self.boss.stop()
        else:
            self.restart()

    def restart(self):
        self.__srv = None
        self.single_view.close()
        self.call('start')

    def has_started(self):
        return self.server is not None
    started = property(has_started)

    def confirm_single_view_controlbar_clicked_close(self, view):
        self.call('close', filename=self.current_file)
        return False


Service = vim_embedded_editor

