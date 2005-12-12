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
import toolbar


class context_toolbar(toolbar.Toolbar):

    def set_contexts(self, contexts):
        self.remove_buttons()
        callbacks = {}
        for name, icon, ltext, func, args in contexts:
            callbacks[name] = func
            self.add_button(name, icon, ltext)
        def clicked(toolbar, name):
            callbacks[name](args)
        self.connect('clicked', clicked)
        self.show_all()

def get_menu(self, contexts, globaldict):
    callbacks = {}
    def clicked(menuitem, name):
        callbacks[name](args)
    menu = gtk.Menu()
    for name, icon, ltext, func, args in contexts:
        callbacks[name] = func
        menuitem = gtk.MenuItem()
        menubox = gtk.HBox(spacing=4)
        icon = icons.icons.get_image(icon)
        menubox.pack_start(icon, expand=False)
        label = gtk.Label(ltext)
        label.set_alignment(0, 0.5)
        menubox.pack_start(label)
        menuitem.add(menubox)
        menu.append(menuitem)
        menuitem.connect('activate', clicked, name)
        menu.show_all()
        return menu
