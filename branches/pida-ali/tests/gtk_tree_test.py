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

import _base
import pida.pidagtk.tree as tree

class TreeTestCase(_base.WidgetTestCase):
    WIDGET = tree.Tree
    WIDGET_ARGS = []

    def test_a_clear(self):
        self.widget.add_item(tree.TreeItem('1', '1'))
        self.widget.clear()
        self.assert_(len(self.widget.model) == 0)

    def test_b_add_item(self):
        self.widget.add_item(tree.TreeItem('1', '1'))
        niter = self.widget.model.get_iter_first()
        self.assert_(self.widget.model.get_value(niter, 0) == '1')

    def test_c_add_items(self):
        items = (tree.TreeItem('%s' % i, []) for i in range(20))
        self.widget.add_items(items)
        self.assert_(len(self.widget.model) >= 20)

t = TreeTestCase()
print t.WIDGET
t.run_tests()
_base.gtk.main()
