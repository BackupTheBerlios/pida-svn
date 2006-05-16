# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

# Copyright (c) 2006 Ali Afshar

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

import gtk

from components import PGDSlaveDelegate

from tree import Tree
from icons import icons

class StackItem(object):

    def __init__(self, index, filename, linenumber, function, line):
        self.key = index
        self.filename = filename
        self.basename = os.path.basename(filename)
        self.dirname = os.path.dirname(filename)
        self.linenumber = linenumber
        self.funcion = function
        self.line = line
        self.active=False

    def get_color(self):
        if self.active:
            return '#000000'
        else:
            return '#909090'
    color = property(get_color)

    def get_icon(self):
        if self.active:
            return None#icons.get(gtk.STOCK_EXECUTE, 16)
        else:
            return None

    pixbuf = property(get_icon)


class StackViewer(PGDSlaveDelegate):

    def create_toplevel_widget(self):
        toplevel = gtk.VBox()
        t = self.add_widget('tree', Tree())
        t.set_property('markup-format-string',
                       '<span color="%(color)s">'
                       '<b>%(basename)s:%(linenumber)s</b> '
                       '<i><small>%(dirname)s</small></i>\n'
                       '<tt>%(line)s</tt></span>')
        t.view.set_expander_column(t.view.get_column(1))
        toplevel.pack_start(t)
        return toplevel

    def attach_slaves(self):
        self.main_window.attach_slave('stack_holder', self)
        self.show_all()

    def update_stack(self, stack):
        self._current_tid = stack['current tid']
        self.tree.clear()
        for i, row in enumerate(stack['stack'][::-1][:-2]):
            fn, ln, fc, tl = row
            stack_item = StackItem(i, fn, ln, fc, tl)
            if i == 0:
                stack_item.active = True
            self.tree.add_item(stack_item)
    
    def select_frame(self, index):
        for i, row in enumerate(self.tree.model):
            val = row[1].value
            val.active = (i == index)
            val.reset_markup()

    def on_tree__double_clicked(self, tv, item):
        index = item.key
        self.session_manager.set_frame_index(index)


