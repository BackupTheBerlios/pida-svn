# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

# Copyright (c) 2006 Ali Afshar

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


def set_stock_icons(st_req, st_path):
    import pkg_resources as pr
    pidareq = pr.Requirement.parse(st_req)
    icon_names = pr.resource_listdir(pidareq, st_path)
    stock_ids = set(gtk.stock_list_ids())
    iconfactory = gtk.IconFactory()
    theme = gtk.icon_theme_get_default()
    listed = theme.list_icons()
    for icon in icon_names:
        if icon.startswith('.'):
            continue
        iconname = icon.split('.', 1)[0]
        if iconname not in listed:
            iconres = '/'.join(['icons', icon])
            iconpath = pr.resource_filename(pidareq, iconres)
            pixbuf = gtk.gdk.pixbuf_new_from_file(iconpath)
            iconset = gtk.IconSet(pixbuf)
            iconfactory.add(iconname, iconset)
            gtk.icon_theme_add_builtin_icon(iconname, 24, pixbuf)
    iconfactory.add_default()
    return theme, iconfactory

class Icons(object):

    def __init__(self):
        return
        self.theme, self.iconfactory = set_stock_icons('pida', 'icons')

    def get(self, name, size=16):
        return
        return self.theme.load_icon(name, size, 0)

icons = Icons()


