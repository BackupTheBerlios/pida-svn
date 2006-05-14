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


import gobject

# pida core import(s)
import pida.core.service as service

# pida utils import(s)
import pida.utils.vim.vimembed as vimembed
import pida.utils.vim.vimeditor as vimeditor

defs = service.definitions

from pida.model import attrtypes as types

class VimEmbedConfig:
    __order__ = ['vim_command', 'vim_events', 'display']
    class vim_command(defs.optiongroup):
        """Vim command options."""
        __order__ = ['use_cream']
        label = "Commands"
        
        class use_cream(defs.option):
            """Whether Cream for Vim will be used"""
            rtype = types.boolean
            default = False

    class vim_events(defs.optiongroup):
        """How PIDA will react to events from Vim."""
        __order__ = ['shutdown_with_vim']
        label = "Events"
        
        class shutdown_with_vim(defs.option):
            """Whether to shutdown pida with Vim"""
            label = "Quit Pida when Vim quits"
            rtype = types.boolean
            default = False

    class display(defs.optiongroup):
        """Vim display options"""
        __order__ = ['colour_scheme', 'hide_vim_menu']
        label = "Display"
        class colour_scheme(defs.option):
            """The colour scheme to use in vim (Empty will be ignored)."""
            rtype = types.string
            label = "Color scheme:"
            default = ''
        class hide_vim_menu(defs.option):
            """Whether the vim menu will be hidden."""
            rtype = types.boolean
            label = "Hide Vim menu"
            default = False
    __markup__ = lambda self: 'Vim Embedded'


class vim_embedded_editor(vimeditor.vim_editor, service.service):

    display_name = 'Embedded Vim'

    config_definition = VimEmbedConfig

    class Vim(defs.View):
        view_type = vimembed.vim_embed
        book_name = 'edit'

    def init(self):
        self.__srv = None
        self.__view = None
        vimeditor.vim_editor.init(self)

    def get_server(self):
        """Return our only server."""
        return self.__srv
    server = property(get_server)

    def vim_start(self):
        self.__view = self.create_view('Vim')
        if self.opts.vim_command__use_cream:
            command = 'cream'
        else:
            command = 'gvim'
        self.show_view(view=self.__view)
        def _r(command=command):
            self.__view.run(command)
        gobject.idle_add(_r)

    def vim_new_serverlist(self, serverlist):
        if (self.__view is not None and
            self.__view.servername in serverlist and
            not self.started):
            self.__srv = self.__view.servername
            self.vim_window.init_server(self.server)
            self.reset()
            self.__files = {}
            self.get_service('editormanager').events.emit('started')

    def after_shutdown(self, server):
        if self.opts.vim_events__shutdown_with_vim:
            self.boss.stop()
        else:
            self.restart()

    def restart(self):
        self.__srv = None
        self.__view.close()
        self.call('start')

    def has_started(self):
        return self.server is not None
    started = property(has_started)

    def view_confirm_close(self, view):
        doc=self.current_document
        if doc:
            self.call('close', filename=self.current_document.filename)
            return False
        else:
            return True
    def get_single_view(self):
        return self.__view
    single_view = property(get_single_view)


Service = vim_embedded_editor

