# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 George Cristian Bîrzan gcbirzan@wolfheart.ro

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
import pango
import gobject
import pida.plugin as plugin
import pida.gtkextra as gtkextra


class Plugin(plugin.Plugin):
    NAME = "Boss"
    VISIBLE = False

    def init(self):
        self.filetype_triggered = False
        self.filetypes = dict()

    def evt_bufferchange(self, buffernumber, buffername):
        if not self.filetype_triggered:
            self.filetypes[buffernumber] = None
        self.filetype_triggered = False
        print self.filetypes[buffernumber]

        
    def evt_filetype(self, buffernumber, filetype):
        self.filetype_triggered = True
        self.filetypes[buffernumber] = filetype
