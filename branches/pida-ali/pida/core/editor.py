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

def import_editor(name):
    """ Find a named plugin and instantiate it. """
    # import the module
    # The last arg [True] just needs to be non-empty
    try:
        mod = __import__('pida.editors.%s.editor' % name, {}, {}, [True])
        cls = mod.Editor
    except ImportError, e:
        print ('Plugin "%s" failed to import with: %s' % (name, e))
        cls = None
    return cls

import service

class Editor(service.Service):
    """ The editor interface. """
 

    def launch(self):
        """Start the editor."""

    view = None


    def close_buffer(index):
        """Closes this buffer"""

    def close_currentbuffer():
        """Closes the current buffer"""

    def fetch_bufferlist(callback):
        """fetches a list of the buffers, calling the callback with the result"""
 
    def fetch_currentbuffer(callback):
        """fetches the active buffer"""

    def goto_line(line_number):
        """Goes to line number on the active buffer"""

    def goto_column(column_number):
        """Goto the column number of the active buffer"""

    def highlight_line(line_number):
        """Highlight the line of the active buffer"""

    def open_file(self, filename):
        """Opens a file"""

    def close_file(filename):
        """Closes a file"""

    def open_string(stringdata):
        """Open a string in a new buffer"""

    def save_file():
        """Save the current buffer"""

    def save_as_file(filename):
        """Save the current buffer as the filename"""

    def save_buffer_as_file(bufferindex, filename):
        """Save the indexed buffer as the given filename"""


class EditorManager(service.Service):
    NAME = 'editor'
    COMMANDS = [['open-file', [('filename', True)]],
                ['start-editor', []]]
    EVENTS = ['started', 'file-opened', 'current-file-closed']
    BINDINGS = [('buffermanager', 'file-opened')]

    def init(self):
        editor_type = import_editor('culebra')
        editor_type.boss = self.boss
        editor_type.manager = self
        self.__editor = editor_type()

    def populate(self):
        self.__editor.populate()

    def cmd_start_editor(self):
        self.__editor.launch()

    def cmd_open_file(self, filename):
        self.__editor.open_file(filename)

    def evt_buffermanager_file_opened(self, buffer):
        self.__editor.open_file(buffer.filename)

    def __get_view(self):
        return self.__editor.view
    view = property(__get_view)
