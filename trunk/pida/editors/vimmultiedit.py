# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Ali Afshar aafshar@gmail.com

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
import pida.utils.vim.vimcom as vimcom
import pida.utils.vim.vimeditor as vimeditor
import pida.core.service as service
import pida.pidagtk.contentview as contentview
import pida.pidagtk.icons as icons


class vim_plugin_view(gtk.HBox):
    """View holding the vim controls."""

    def __init__(self, service):
        self.service = service
        gtk.HBox.__init__(self, spacing=3)
        icon = icons.icons.get_image('vim')
        self.pack_start(icon, expand=False)
        self.__serverlist = gtk.combo_box_new_text()
        self.pack_start(self.__serverlist)

    def set_serverlist(self, serverlist):
        current = self.__serverlist.get_active_text()
        self.__serverlist.get_model().clear()
        j = 0
        for i, server in enumerate(serverlist):
            self.__serverlist.append_text(server)
            if server == current:
                self.__serverlist.set_active(i)
            j = 1
        if j == 0:
            self.__serverlist.append_text('no vim running')
            self.__serverlist.set_sensitive(False)
        else:
            self.__serverlist.set_sensitive(True)
        if self.__serverlist.get_active() == -1:
            self.__serverlist.set_active(0)
        self.__serverlist.show_all()
    
    def get_current_server(self):
        return self.__serverlist.get_active_text()
    current_server = property(get_current_server)


class vim_multi_editor(vimeditor.vim_editor, service.service):

    display_name = 'External Vim'

    def start(self):
        self.__oldservers = []
        self.view = vim_plugin_view(service=self)
        self.__cw = vimcom.communication_window(self)
        self.view.show_all()
        self.get_service('buffermanager').\
            single_view.widget.pack_start(self.view, expand=False)
        self.get_service('editormanager').events.emit('started')

    def vim_new_serverlist(self, serverlist):
        def _serverlist():
            for server in serverlist:
                if 'PIDA_EMBEDDED' not in server:
                    if server not in self.__oldservers:
                        self.__cw.init_server(server)
                    yield server
        self.view.set_serverlist(_serverlist())
        self.__oldservers = serverlist

    def get_server(self):
        return self.view.current_server
    server = property(get_server)


Service = vim_multi_editor

