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

class BufferTree(tree.Tree):
    
    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Time Opened','creation_time'),
                      ('File path','filename'),
                      ('File name','basename'),
                      ('Mime Type','mimetype'),
                      ('File Length','length'),
                      ('Project', 'project_name')]

    def __init__(self):
        tree.Tree.__init__(self)
        self.view.set_expander_column(self.view.get_column(1))
        self.set_property('markup-format-string', '%(filename)s')
        self.view.set_enable_search(False)
        def _se(model, column, key, iter):
            val = model.get_value(iter, 1).value
            isnt = not val.basename.startswith(key)
            return isnt
        self.view.set_search_equal_func(_se)
        
    def set_bufferlist(self, bufferlist):
        # naive
        self.set_items(self.__adapt_bufferlist(bufferlist))

    def set_currentbuffer(self, filename):
        self.set_selected(filename)



