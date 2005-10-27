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
import os
import pida.core.service as service
import pida.pidagtk.filemanager as filemanager

class FileManager(service.Service):
    NAME = 'filemanager'
    COMMANDS = [('browse', [('directory', True),
                            ('filters', False),
                            ('glob', False)])]

    def init(self):
        self.__content = None

    def cmd_browse(self, directory, filters=[], glob='*'):
        if self.__content is None:
            content = filemanager.FileBrowser()
            def activated(filebrowser, filename):
                self.boss.command('buffermanager', 'open-file', filename=filename)
            def changed(filebrowser, dirname):
                def setstatuses(statuses):
                    filebrowser.set_statuses(statuses)
                self.boss.command('versioncontrol', 'get-statuses',
                    datacallback=setstatuses,
                    directory=dirname)
            content.connect('file-activated', activated)
            content.connect('directory-changed', changed)
            self.__content = content
            self.__content.connect('removed', self.cb_content_removed)
            self.boss.command('contentbook', 'add-page', contentview=content)
            directory = os.path.expanduser('~')
        if directory != '':
            self.__content.display(directory)
        self.__content.raise_tab()

    def cb_content_removed(self, contentview):
        self.__content.emit_stop_by_name('removed')
        self.__content = None

Service = FileManager
