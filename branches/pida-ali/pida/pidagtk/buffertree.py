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

import tree
import gtk

class BufferItem(tree.IconTreeItem):

    def __get_markup(self):
        """Return the markup for the item."""
        return self.value.filename
    markup = property(__get_markup)
    

class BufferTree(tree.IconTree):
    
    def __init__(self):
        tree.IconTree.__init__(self)
        self.__bufferdetails = BufferDetails()
        self.pack_start(self.__bufferdetails, expand=False)
        
    def set_bufferlist(self, bufferlist):
        # naive
        self.set_items(self.__adapt_bufferlist(bufferlist))

    def set_currentbuffer(self, filename):
        self.set_selected(filename)

    def display_buffer(self, buf):
        self.__bufferdetails.display_buffer(buf)

    def __adapt_bufferlist(self, bufferlist):
        for buf in bufferlist:
            yield self.__adapt_buffer(bufferlist[buf])

    def __adapt_buffer(self, buf):
        return BufferItem(buf.filename, buf, None)


class BufferDetails(gtk.Label):

    def __init__(self):
        gtk.Label.__init__(self)
    
    def display_buffer(self, buf):
        self.set_markup(buf.filename)
