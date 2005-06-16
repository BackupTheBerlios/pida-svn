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

class IPWindow(object):
    
    def __init__(self, pb):
        self.pb = pb
        self.rw = gtk.Window()
        self.rw.realize()
        self.rw.add_events(gtk.gdk.PROPERTY_CHANGE_MASK)
        self.rw.connect('property-notify-event', self.cb_r)

    def reset(self, id):
        self.ww = gtk.gdk.window_foreign_new(id)

    def write(self, property, value, ptype=32):
        self.ww.property_change(property, gtk.gdk.SELECTION_TYPE_STRING,
                                ptype,
                                gtk.gdk.PROP_MODE_REPLACE,
                                value)

    def connect(self):
        self.write('connect', [self.rw.window.xid])
        
    def cb_r(self, window, ev):
        if hasattr(ev, 'atom'):
            message = self.rw.window.property_get(ev.atom, pdelete=True)
            if message and ev.atom[0].islower():
                self.do(ev, message)

    def do(self, ev, message):
                self.pre_do()
                c = 'do_%s' % ev.atom
                v = message[-1]
                if hasattr(self.pb, c):
                    getattr(self.pb, c)(v)
                else:
                    getattr(self, c, lambda a: None)(v)

    def pre_do(self):
        pass

    def do_connect(self, cid):
        self.reset(long(cid[0]))

    def get_lid(self):
        return self.rw.window.xid

    def get_rid(self):
        return self.ww.xid
