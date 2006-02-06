# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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

class ShiftPaned(gtk.VBox):

    def __init__(self, paned_factory=gtk.HPaned, main_first=True):
        super(ShiftPaned, self).__init__()
        self.paned = paned_factory()
        self.paned.show()
        self.main_first = main_first
        self.add(self.paned)
        self.__nonmain = None
        self.__nonmain_args = None
        self.__nonmain_kw = None
        self._visible = True

    def pack_main(self, widget, *args, **kw):
        if self.main_first:
            packer = self.paned.pack1
        else:
            packer = self.paned.pack2
        packer(widget, *args, **kw)

    def pack_sub(self, widget, *args, **kw):
        self.__nonmain = widget
        self.__nonmain_args = args
        self.__nonmain_kw = kw
        self.update_children()

    def update_children(self):
        if self._visible:
            if self.__nonmain:
                if self.main_first:
                    packer = self.paned.pack2
                else:
                    packer = self.paned.pack1
                packer(self.__nonmain, *self.__nonmain_args, **self.__nonmain_kw)
        else:
            self.paned.remove(self.__nonmain)
    
    def show_sub(self):
        self._visible = True
        self.update_children()

    def hide_sub(self):
        self._visible = False
        self.update_children()

    def set_position(self, position):
        self.paned.set_position(position)

if __name__ == '__main__':
    #p = ShiftPaned(gtk.VPaned)
    p = ShiftPaned(gtk.HPaned)
    btn1 = gtk.Label("Show right only")
    btn2 = gtk.ToggleButton("Show left only")
    p.pack_sub(btn1)
    p.pack_main(btn2)
    def on_click(btn):
        if btn.get_active():
            p.show_sub()
        else:
            p.hide_sub()
    btn2.connect("toggled", on_click)
    btn1.show()
    btn2.show()
    w = gtk.Window()
    w.add(p)
    w.show_all()
    w.connect("delete-event", gtk.main_quit)
    gtk.main()


