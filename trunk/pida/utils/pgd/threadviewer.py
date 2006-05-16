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


from tree import Tree

import gtk

from components import PGDSlaveDelegate

from winpdb.rpdb2 import DICT_KEY_TID, DICT_KEY_BROKEN

class ThreadItem(object):
    
    def __init__(self, tdict):
        self.tid = tdict[DICT_KEY_TID]
        self.broken = tdict[DICT_KEY_BROKEN]
        self.is_current = False
        self.key = self.tid

    def get_broken_text(self):
        if self.broken:
            return 'broken'
        else:
            return 'running'
    state = property(get_broken_text)

    def get_pixbuf(self):
        return None
    pixbuf = property(get_pixbuf)


class ThreadsViewer(PGDSlaveDelegate):
        
    def create_toplevel_widget(self):
        exp = gtk.Expander()
        l = gtk.Label()
        l.set_markup('<big>Threads</big>')
        exp.set_label_widget(l)
        exp.set_expanded(True)
        t = self.add_widget('tree', Tree())
        t.set_property('markup-format-string',
            '<tt>%(tid)s</tt> '
            '<span color="#909090"><i>%(state)s</i></span>')
        exp.add(t)
        v = self.add_widget('tree_view', t.view)
        return exp
    
    def attach_slaves(self):
        self.main_window.attach_slave('threads_holder', self)
        self.show_all()

    def update_threads(self, threads_list, current_thread):
        self.tree.clear()
        for tdict in threads_list:
            item = ThreadItem(tdict)
            if item.tid == current_thread:
                item.is_current = True
            self.tree.add_item(item)

    def broken_thread(self, tid):
        for row in self.tree.model:
            if row[0] == tid:
                val = row[1].value()
                val.broken = True
                val.reset_markup()

