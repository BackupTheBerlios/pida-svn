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

# System imports
import os
import time
# GTK imports
import gtk
import gobject
# Pida imports
import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.configuration.registry as registry

import edit

class Plugin(plugin.Plugin):
    NAME = 'Culebra'    

    def init(self):
        self.editor = None
        self.bufferlist = None

    def launch(self):
        if not self.editor:
            self.editor = edit.EditWindow(self.cb)
            self.cb.embedwindow.add(self.editor)
            self.editor.show_all()
        self.edit_getbufferlist()

    def populate_widgets(self):
        pass

    def cb_alternative(self, *args):
        self.cb.action_showconfig()
    
    def evt_started(self):
        self.launch()
        
    def edit_getbufferlist(self):
        bl = [t for t in enumerate([self.abspath(n) for n in \
                                    self.editor.wins.keys()])]
        self.bufferlist = bl
        self.cb.evt('bufferlist', bl)

    def abspath(self, filename):
        if not filename.startswith('/'):
            filename = os.path.join(os.getcwd(), filename)
        return filename

    def edit_getcurrentbuffer(self):
        return self.abspath(self.editor.get_current()[0])
