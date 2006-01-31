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
import toolbar
import os
import pida.core.base as base
class BufferItem(tree.IconTreeItem):

    def __get_markup(self):
        return self.value.markup
    markup = property(__get_markup)


class BufferTree(tree.Tree):
    
    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Time Opened','creation_time'),
                      ('File path','filename'),
                      ('File name','basename'),
                      ('Mime Type','mimetype'),
                      ('File Length','length')]

    def __init__(self):
        tree.Tree.__init__(self)
        self.set_property('markup-format-string', '%(filename)s')
        self.__bufferdetails = BufferDetails()
        #self.pack_start(self.__bufferdetails, expand=False)
        
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
        return BufferItem(buf.filename, buf, buf.icon)

    def get_details_box(self):
        return self.__bufferdetails
    details_box = property(get_details_box)

class BufferDetails(gtk.VBox):

    def __init__(self):
        gtk.VBox.__init__(self)
        self.__toolbar = None
        self.__contextbars = []
        self.__toolbarholder = gtk.HBox()
        self.pack_start(self.__toolbarholder, expand=False)
        self.__title = gtk.Label()
        self.pack_start(self.__title)
    
    def display_buffer(self, buf):
        self.__currentbuffer = buf
        if self.__toolbar is not None:
            self.__toolbarholder.remove(self.__toolbar)
            for bar in self.__contextbars:
                self.__toolbarholder.remove(bar)
        self.__create_toolbar(buf)

    def __create_toolbar(self, buf):
        globaldict={'filename':buf.filename}
        self.__contextbars = []
        def remove(toolbar):
            self.__toolbarholder.remove(toolbar)
        self.__toolbarholder.foreach(remove)
        for context in buf.contexts:
            contextbar = buf.boss.command('contexts', 'get-toolbar',
                                             contextname=context,
                                             globaldict=globaldict)
            self.__contextbars.append(contextbar)
            self.__toolbarholder.pack_start(contextbar, expand=False)
        self.show_all()
        self.__title.set_markup(buf.markup)
