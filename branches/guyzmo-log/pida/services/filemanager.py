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

class file_manager(service.service):
    NAME = 'filemanager'

    single_view_type = filemanager.FileBrowser
    single_view_book = 'content'

    def init(self):
        self.__content = None

    def cmd_browse(self, directory=''):
        if self.single_view is None:
            self.create_single_view()
            self.single_view.connect('file-activated',
                                     self.cb_single_view_file_activated)
        if directory == '':
            directory = os.path.expanduser('~')
        self.single_view.display(directory)

    def cmd_get_current_directory(self):
        if self.single_view is not None:
            return self.single_view.directory

    def cb_single_view_file_activated(self, view, filename):
        
        self.boss.call_command('buffermanager', 'open_file',
                                filename=filename)
        
Service = file_manager
