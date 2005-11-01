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
import tree
import icons
import gobject
import contentbook

def shorten_home_name(directory):
    return directory.replace(os.path.expanduser('~'), '~')

class FileTreeItem(tree.IconTreeItem):
    DIRECTORY = False
    def __get_markup(self):
        return ('<span size="small" foreground="black"><tt>%s</tt></span>' %
                (self.value[:10]))
    markup = property(__get_markup)


class DirTreeItem(tree.IconTreeItem):
    DIRECTORY = True
    def __get_markup(self):
        return ('<span size="small" color="blue"><tt>%s</tt></span>' %
                (self.value[:10]))
    markup = property(__get_markup)

class FileTree(gtk.IconView):
    FIELDS =   (gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_BOOLEAN,
                gtk.gdk.Pixbuf)

    def __init__(self):
        gtk.IconView.__init__(self)
        self.__model = gtk.ListStore(*self.FIELDS)
        self.set_model(self.__model)
        self.set_markup_column(1)
        self.set_pixbuf_column(-1)
        #self.set_orientation(gtk.ORIENTATION_HORIZONTAL)


    def add_item(self, item):
        filename = item.key
        markup = item.markup
        pixbuf = item.pixbuf
        isdir = item.DIRECTORY
        self.__model.append([filename, markup, isdir, pixbuf])

    def clear(self):
        self.__model.clear()

    def get_model(self):
        return self.__model
    model = property(get_model)

DIR_ICON = icons.icons.get_image('filebrowser')

class FileBrowser(contentbook.ContentView):

    __gsignals__ = {'directory-changed' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT, )),
                    'file-activated' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT, ))}

    ICON = 'filemanager'
    ICON_TEXT = 'files'

    def populate(self):
        hbox = gtk.HPaned()
        self.pack_start(hbox)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack2(sw)
        self.__fileview = FileTree()
        sw.add(self.__fileview)
        self.__fileview.connect('item-activated', self.cb_file_activated)
        #self.__dirview.connect('double-clicked', self.cb_dir_activated)
        self.__currentdirectory = None
        add_but = self.add_button("up", "up", 'go to the parent directory')
        add_but = self.add_button("find", "find", 'find things here')


    def display(self, directory, statuses=[], glob='*', hidden=True):
        
        if os.path.isdir(directory):
            self.__currentdirectory = directory
            self.set_title(shorten_home_name(directory))
            self.__fileview.clear()
            for filename in os.listdir(directory):
                path = os.path.join(self.__currentdirectory, filename)
                if os.path.isdir(path):
                    i = DirTreeItem(path, filename, image=DIR_ICON)
                    self.__fileview.add_item(i)
                else:
                    i = FileTreeItem(path, filename)
                    self.__fileview.add_item(i)
            self.emit('directory-changed', directory)


    def go_up(self):
        if self.__currentdirectory and self.__currentdirectory != '/':
            parent = os.path.split(self.__currentdirectory)[0]
            self.display(parent)

    def set_statuses(self, statuses):
        for row in self.__fileview.model:
            if row[0] in statuses:
                niter = row.iter
                column = 3
                self.__fileview.set(niter, column, statuses[row[0]])

    def cb_file_activated(self, view, path):
        niter = self.__fileview.model.get_iter(path)
        if niter:
            filepath = self.__fileview.model.get_value(niter, 0)
            print filepath
            if self.__fileview.model.get_value(niter, 2):
                self.display(filepath)
            else:
                self.emit('file-activated', filepath)

    def cb_dir_activated(self, tree, item):
        self.display(item.key)

    def cb_toolbar_clicked(self, toolbar, name):
        funcname = 'toolbar_action_%s' % name
        if hasattr(self, funcname):
            func = getattr(self, funcname)
            func()

    def toolbar_action_up(self):
        self.go_up()

    def toolbar_action_find(self):
        if self.__currentdirectory is not None:
            self.boss.command('grepper', 'find-interactive',
                               directories=[self.__currentdirectory])

if __name__ == '__main__':
    w = gtk.Window()
    f = FileBrowser()
    w.add(f)
    w.show_all()
    f.display('/home/ali')
    gtk.main()
        
