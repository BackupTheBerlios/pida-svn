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
import gobject
import contentbook

def shorten_home_name(directory):
    return directory.replace(os.path.expanduser('~'), '~')

class FileTreeItem(tree.TreeItem):
    pass
    def __get_markup(self):
        return '<span size="small" foreground="black">%s</span>' % (self.value)
    markup = property(__get_markup)


class DirTreeItem(tree.TreeItem):
    def __get_markup(self):
        return '<span size="small" foreground="blue">%s/</span>' % (self.value)
    markup = property(__get_markup)


class FileTree(tree.Tree):
    FIELDS =   (gobject.TYPE_STRING,
              gobject.TYPE_PYOBJECT,
              gobject.TYPE_STRING,
              gobject.TYPE_STRING)
    
    COLUMNS = [[gtk.CellRendererText, 'markup', 3],
               [gtk.CellRendererText, 'markup', 2]]

    def add_item(self, item, parent=None):
        filename = item.value
        markup = item.markup
        self.model.append(parent, [filename, item, markup, ''])


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
        self.__dirview = FileTree()
        hbox.pack1(self.__dirview, False, False)
        self.__fileview = FileTree()
        hbox.pack2(self.__fileview, False, False)
        self.__fileview.connect('double-clicked', self.cb_file_activated)
        self.__dirview.connect('double-clicked', self.cb_dir_activated)
        self.__currentdirectory = None
        add_but = self.add_button("up", "up", 'go to the parent directory')


    def display(self, directory, statuses=[], glob='*', hidden=True):
        
        if os.path.isdir(directory):
            self.__currentdirectory = directory
            self.set_title(shorten_home_name(directory))
            self.__fileview.clear()
            self.__dirview.clear()
            for filename in os.listdir(directory):
                path = os.path.join(self.__currentdirectory, filename)
                if os.path.isdir(path):
                    i = DirTreeItem(path, filename)
                    self.__dirview.add_item(i)
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

    def cb_file_activated(self, tree, item):
        newpath = item.key
        self.emit('file-activated', newpath)

    def cb_dir_activated(self, tree, item):
        self.display(item.key)

    def cb_toolbar_clicked(self, toolbar, name):
        funcname = 'toolbar_action_%s' % name
        if hasattr(self, funcname):
            func = getattr(self, funcname)
            func()

    def toolbar_action_up(self):
        self.go_up()

if __name__ == '__main__':
    w = gtk.Window()
    f = FileBrowser()
    w.add(f)
    w.show_all()
    f.display('/home/ali')
    gtk.main()
        
