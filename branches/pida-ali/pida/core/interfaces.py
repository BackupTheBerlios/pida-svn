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

from protocols import Interface

class IArgument(Interface):

    def get_name():
        """Return the argument name."""

    def get_required():
        """Return whether the argument is required."""

class ICommand(Interface):

    def get_name():
        """Return the name of the command."""
    
    def get_group():
        """Return the group that the command is in."""

    def get_args():
        """Return a list of IArgument for the command."""

    def __call__(**kw):
        """Call the command with the keyword args."""

class IEditor(Interface):
    """ The editor interface. """
    def change_buffer(index):
        """Makes the buffer indentified by 'index' active."""
 
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

    def open_file(filename):
        """Opens a file"""

    def open_string(stringdata):
        """Open a string in a new buffer"""

    def save_file():
        """Save the current buffer"""

    def save_as_file(filename):
        """Save the current buffer as the filename"""

    def save_buffer_as_file(bufferindex, filename):
        """Save the indexed buffer as the given filename"""

class IBuffer:
    def get_is_new():
        """Returns wether a file is a new one"""
  
    def get_type(self):
        """Returns the buffer type"""
 
    def get_filename (self):
        """Returns the filename associated with this buffer"""

class IRegistryItem:
    pass

class IComponent:
    pass

class IService:
    pass

class IPlugin:
    pass

class ILogger:
    pass

