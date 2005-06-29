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


import pida.plugin as plugin
import gazpachembed
import gtk

class Plugin(plugin.Plugin):
    NAME = 'Gazpacho'

    def populate_widgets(self):
        
        self.holder = gtk.VBox()
        self.add(self.holder)
        self.gazpacho = None
        self.menu = None


    def cb_alternative(self, *args):
        self.launch()

    def launch(self):
        if not self.gazpacho:
            self.gazpacho = gazpachembed.Gazpacho(self.cb)
        self.gazpacho.launch(self.holder)
        if not self.menu:
            self.menu = self.gazpacho.app.menu
            self.cusbar.win.pack_start(self.menu, expand=False)
    

    #def evt_started(self, *args):
    #    self.launch()
