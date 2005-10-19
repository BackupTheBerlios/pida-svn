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
import gobject
import icons
class Toolbar(gtk.HBox):

    
    __gsignals__ = {'clicked' : (
                    gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE,
                    (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):
        gtk.HBox.__init__(self)

    def add_button(self, name, icon, tooltip='None Set!', text=False):
        evt = gtk.EventBox()
        if text:
            but = icons.icons.get_text_button(icon, name)
        else:
            but = icons.icons.get_button(icon)
        evt.add(but)
        icons.tips.set_tip(evt, tooltip)
        but.connect('clicked', self.cb_clicked, name)
        self.pack_start(evt, expand=False, padding=0)
        but.show_all()
        return but

    def add_separator(self):
        sep = gtk.VSeparator()
        self.pack_start(sep, padding=0, expand=False)

    def cb_clicked(self, button, name):
        self.emit('clicked', name)
