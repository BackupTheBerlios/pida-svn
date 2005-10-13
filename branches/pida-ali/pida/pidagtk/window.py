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

import gtk


class PidaWindow(gtk.Window):

    def __init__(self):
        """Initialise the window."""
        gtk.Window.__init__(self)
        self.__p0 = gtk.HPaned()
        self.add(self.__p0)
        self.__p1 = gtk.VPaned()
        self.__p0.pack1(self.__p1)
        self.__p2 = gtk.VPaned()
        self.__p0.pack2(self.__p2)
        self.__pS = None

    def __packTL(self, widget):
        """Pack the widget in the top-left pane."""
        self.__p1.pack1(widget)

    def __packBL(self, widget):
        """Pack the widget in the top-left pane."""
        self.__p1.pack2(widget)

    def __packTR(self, widget):
        """Pack the widget in the top-left pane."""
        self.__p2.pack1(widget)

    def __packBR(self, widget):
        """Pack the widget in the top-left pane."""
        self.__p2.pack2(widget)

    def __pack_sidebar(self, w1, w2, horizontal):
        """Create and pack the sidebar with the widgets."""
        if horizontal:
            self.__pS = gtk.HPaned()
        else:
            self.__pS = gtk.VPaned()
        self.__pS.pack1(w1)
        self.__pS.pack2(w2)

    def pack(self, editor, bufferlist, pluginbook, contentbook,
            sidebar_orientation_horizontal,
            sidebar_on_right,
            contentbook_on_right):
        """Pack the required components."""
        self.__pack_sidebar(bufferlist, pluginbook,
            sidebar_orientation_horizontal)
        if sidebar_on_right:
            self.__packTR(self.__pS)
            self.__packTL(editor)
        else:
            self.__packTL(self.__pS)
            self.__packTR(editor)
        if contentbook_on_right:
            self.__packBR(contentbook)
        else:
            self.__packBL(contentbook)
            
    def pack_bl_only(self, bufferlist):
        self.pack(fake('ed'), bufferlist, fake('pb'), fake('cb'), True, True, True)
        bufferlist.set_size_request(400, 400)

    def pack_bl_ed(self, ed, bl):
        self.pack(ed, bl, fake('pb'), fake('cb'), True, True, True)
        bl.set_size_request(400, 400)

    def pack_ed_bl_cb(self, ed, bl, cb):
        self.pack(ed, bl, fake('pb'), cb, True, True, True)
        bl.set_size_request(400, 400)
    

import unittest
class test_window(unittest.TestCase):
    
    def test_main_window(self):
        w = PidaWindow()
        w.pack(fake('ed'), fake('bl'), fake('pb'), fake('cb'), True, True, True)
        gtk.main()

class fake(object):
    def __init__(self, s):
        self.win = gtk.Label(s)

def test():
    unittest.main()

if __name__ == '__main__':
    test()
