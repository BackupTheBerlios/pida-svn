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
import shelve

class Icons(object):

    def __init__(self, icon_file=None):
        icon_file = ('/home/ali/working/pida/pida/branches/'
                     'pida-ali/pida/pidagtk/icons.dat')
        self.d = shelve.open(icon_file, 'r')
        self.cs = gtk.gdk.COLORSPACE_RGB
    
    def get(self, name, *args):
        if name not in  self.d:
            name = 'new'
        d, a = self.d[name]
        pb = gtk.gdk.pixbuf_new_from_data(d, self.cs, *a)
        return pb

    def get_image(self, name, *size):
        im = gtk.Image()
        im.set_from_pixbuf(self.get(name))
        return im

    def get_button(self, name, *asize):
        ic = self.get_image(name)
        but = gtk.ToolButton(icon_widget=ic)
        return but

    def get_text_button(self, icon, text):
        ic = self.get_image(icon)
        il = gtk.Label(text)
        ib = gtk.HBox()
        ib.pack_start(ic)
        ib.pack_start(il)
        but = gtk.ToolButton(icon_widget=ib)
        return but


tips = gtk.Tooltips()
tips.enable()

icons = Icons()
