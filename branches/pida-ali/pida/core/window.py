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

import service
import commands
import pida.pidagtk.window as window

class WindowManager(service.Service):
    """Class to control the main window."""
    NAME = 'window'
    COMMANDS = [['set-title', [('title', True)]]]
    
    def init(self):
        self.__window = window.PidaWindow()
        self.__window.connect('destroy', self.cb_destroy)

    def cb_destroy(self, window):
        self.boss.stop()

    def populate(self):
        """Populate the window."""
        bufferview = self.boss.get_service('buffermanager').view
        contentbook = self.boss.get_service('contentbook').view
        viewbook = self.boss.get_service('viewbook').view
        topbar = self.boss.get_service('topbar').view
        pluginmanager = self.boss.plugins.view
        editor = self.boss.get_editor().view
        self.__window.pack(editor, bufferview, pluginmanager, contentbook,
            viewbook, topbar, False, True)

    def reset(self):
        """Display the window."""
        self.__window.show_all()

    def __get_view(self):
        return self.__window
    view = property(__get_view)

    def cmd_settitle(self, title):
        """Set the window title.
        
        title: a string representation of the new title."""
        self.__window.set_title(title)
