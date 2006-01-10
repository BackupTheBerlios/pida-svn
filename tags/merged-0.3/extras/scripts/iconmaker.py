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

import os
import gtk
import shelve
import shutil

I = gtk.IconTheme()
I.set_custom_theme('Humility')


f = open('iconmaker.data', 'r')
try:
    shutil.rmtree('iconbuild')
except:
    pass
try:
    os.remove('icons.dat')
except:
    pass
os.mkdir('iconbuild')
outfile = shelve.open('icons.dat')
for line in f:
    if line.startswith('#'):
        continue
    name, key = [s.strip() for s in line.split(' ')]
    i = I.load_icon(name, 15, 0)
    d = i.get_pixels()
    cs = i.get_colorspace()
    ha = i.get_has_alpha()
    bp = i.get_bits_per_sample()
    w = i.get_width()
    h = i.get_height()
    rs = i.get_rowstride()
    outfile[key] = d, (ha, bp, w, h, rs)
outfile.close()
w = gtk.Window()
w.connect('destroy', gtk.main_quit)
b = gtk.HBox()
w.add(b)
outfile = shelve.open('icons.dat')
cs = gtk.gdk.COLORSPACE_RGB
for i in outfile:
    d, a = outfile[i]
    pb = gtk.gdk.pixbuf_new_from_data(d, cs, *a)
    im = gtk.Image()
    im.set_from_pixbuf(pb)
    b.pack_start(im)
outfile.close()
w.show_all()
gtk.main()

