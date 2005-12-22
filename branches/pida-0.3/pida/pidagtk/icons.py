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

defaulticons = gtk.icon_theme_get_default()

class Icons(object):

    def __init__(self, icon_file=None):
        #icon_file = ('/home/ali/working/pida/pida/branches/'
        #             'pida-ali/pida/pidagtk/icons.dat')
        from pkg_resources import Requirement, resource_filename
        icon_file = resource_filename(Requirement.parse('pida'), 'images/icons.dat')
        #icon_file = "/usr/share/pida/icons.dat"
        self.d = shelve.open(icon_file, 'r')
        self.cs = gtk.gdk.COLORSPACE_RGB
        stock_ids = set(gtk.stock_list_ids())
        iconfactory = gtk.IconFactory()
        self.__theme = gtk.icon_theme_get_default()
        for k in self.d:
            stockname = 'gtk-%s' % k
            if stockname not in stock_ids:
                d, a = self.d[k]
                pixbuf = gtk.gdk.pixbuf_new_from_data(d, self.cs, *a)
                iconset = gtk.IconSet(pixbuf)
                iconfactory.add(stockname, iconset)
                gtk.icon_theme_add_builtin_icon(stockname, 12, pixbuf)
        iconfactory.add_default()
        self.__iconfactory = iconfactory

    def get(self, name, *args):
        try:
            print name, 'found'
            return self.__theme.load_icon('gtk-%s' % name, 12, 0)
        except:
            print name, 'notfound'
            return self.__theme.load_icon('gtk-manhole', 12, 0)
            
    def get_image(self, name, *size):
        im = gtk.Image()
        im.set_from_pixbuf(self.get(name))
        return im

    def get_mime_image(self, mimetype):
        def load_icon(name):
            try:
                ic = defaulticons.load_icon(name, 14, 1)
            except:
                ic = None
            return ic
        ic = None
        if mimetype:
            major, minor = mimetype.split('/', 1)
            t1 = 'gnome-mime-%s-%s' % (major, minor)
            t2 = 'gnome-mime-application-%s' % minor
            t3 = 'gnome-mime-%s' % major
            for t in [t1, t1]:
                ic = load_icon(t)
                if ic:
                    break
        if not ic:
            ic = None#self.get('gtk-new')
        return ic

    def get_button(self, name, tooltip='', *asize):
        ic = self.get_image(name)
        but = gtk.ToolButton(icon_widget=ic)
        #but = gtk.ToolButton(stock_id='gtk-%s' % name)
        #but.set_size_request(32, 32)
        return but

    def get_text_button(self, icon, text):
        ic = self.get_image(icon)
        il = gtk.Label()
        il.set_markup('<span>%s</span>' % text)
        ib = gtk.HBox(spacing=2)
        ib.pack_start(ic)
        ib.pack_start(il)
        but = gtk.ToolButton(icon_widget=ib)
        return but


tips = gtk.Tooltips()
tips.enable()

icons = Icons()
