# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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
import os
import pida.core.service as service
import pida.pidagtk.filemanager as filemanager
import pida.core.actions as actions

defs = service.definitions

class file_manager(service.service):

    plugin_view_type = filemanager.FileBrowser

    class directory_changed(defs.event):
        """Called when the current directory is changed."""

    def init(self):
        self.__content = None

    @actions.action(
    default_accel='<Control><Shift>f',
    label='Focus the file manager'
    )
    def act_grab_focus(self, action):
        self.call('browse', directory=self.cmd_get_current_directory())

    def act_open(self, action):
        """Open the current file in the editor."""
        self.boss.call_command('buffermanager', 'open_file',
                               filename=self.plugin_view.selected)

    def cmd_browse(self, directory=None):
        #if self.plugin_view is None:
        #    self.create_plugin_view()
        self.plugin_view.connect('file-activated',
                                  self.cb_single_view_file_activated)
        if directory is None:
            directory = os.path.expanduser('~')
        self.plugin_view.display(directory)
        self.plugin_view.raise_page()

    def cmd_get_current_directory(self):
        return self.plugin_view.directory

    def cb_single_view_file_activated(self, view, filename):
        
        self.boss.call_command('buffermanager', 'open_file',
                                filename=filename)

        
Service = file_manager
