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
import threading
import contentview
import mimetypes
import contextwidgets

def shorten_home_name(directory):
    return directory.replace(os.path.expanduser('~'), '~')

class FileTreeItem(tree.IconTreeItem):
    def __get_markup(self):
        return ('<span foreground="black"><tt>%s</tt></span>' %
                (self.value.name))
    markup = property(__get_markup)


class DirTreeItem(tree.IconTreeItem):
    def __get_markup(self):
        return ('<span color="blue"><tt>%s</tt></span>' %
                (self.value.name))
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

DIR_ICON = icons.icons.get_image('filemanager')

class FileTree(tree.IconTree):

    SORT_LIST = ['directory', 'name']

    def clear(self):
        self.model.clear()

    def clear_nodes(self, iters):
        for iter in iters:
            self.model.remove(iter)

    def get_node_children(self, piter):
        children = []
        for i in xrange(self.model.iter_n_children(piter)):
            children.append(self.model.iter_nth_child(piter, i))
        return children

    def __init__(self, fm):
        tree.IconTree.__init__(self)
        self.__fm = fm
        self.view.connect('row-expanded', self.cb_row_expanded)

    def cb_row_expanded(self, view, titer, path):
        item = self.get(titer, 1).value
        self.__fm.display(item.path, rootpath=path)
        return True

class FileSystemItem(object):

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)

class FileBrowser(contentview.content_view):

    __gsignals__ = {'directory-changed' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT, )),
                    'file-activated' : (
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_NONE,
                        (gobject.TYPE_PYOBJECT, ))}

    ICON_NAME = 'filemanager'
    ICON_TEXT = 'files'

    def init(self):
        self.__toolbar = contextwidgets.context_toolbar()
        self.widget.pack_start(self.__toolbar, expand=False)
        hbox = gtk.HPaned()
        self.widget.pack_start(hbox)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack2(sw)
        self.__fileview = FileTree(self)
        sw.add(self.__fileview)
        #self.__fileview.connect('item-activated', self.cb_file_activated)
        self.__fileview.connect('double-clicked', self.cb_file_activated)
        self.__fileview.connect('right-clicked', self.cb_file_rightclicked)
        self.__currentdirectory = None
        #add_but = self.add_button("up", "up", 'go to the parent directory')
        #add_but = self.add_button("new", "new", 'Create a new file here')
        #add_but = self.add_button("find", "find", 'find things here')

    def display(self, directory, rootpath=None, statuses=[], glob='*', hidden=True):
        if os.path.isdir(directory):
            childnodes = []
            def get_root():
                if rootpath is None:
                    return None
                else:
                    return self.__fileview.model.get_iter(rootpath)
            if rootpath is None:
                self.set_long_title(shorten_home_name(directory))
                self.__currentdirectory = directory
                globaldict = {'directory':directory}
                contexts = self.service.boss.call_command('contexts',
                                                  'get_contexts',
                                                  contextname='directory',
                                                  globaldict=globaldict)
                self.__toolbar.set_contexts(contexts)
                #tb = self.boss.command('contexts', 'get-toolbar',
                #                       contextname='directory',
                #                       globaldict={'directory': directory})
                #for child in self.bar_area.get_children():
                #    self.bar_area.remove(child)
                #    child.destroy()
                #self.bar_area.pack_start(tb, expand=False)
                self.__fileview.clear()
            else:
                for i in xrange(0,
                    self.__fileview.model.iter_n_children(get_root())):
                    child = self.__fileview.model.iter_nth_child(
                        get_root(), i)
                    childpath = self.__fileview.model.get_path(child)
                    childnodes.append(childpath)
            def listdir():
                images = {}
                for filename in os.listdir(directory):
                    path = os.path.join(directory, filename)
                    fsi = FileSystemItem(path)
                    if os.path.isdir(path):
                        fsi.directory = -1
                        i = DirTreeItem(path, fsi, image=DIR_ICON)
                        item = self.__fileview.add_item(i, get_root())
                        childfsi = FileSystemItem('empty')
                        i2 = FileTreeItem('', fsi)
                        self.__fileview.add_item(i2, item)
                    else:
                        fsi.directory = 0
                        mtype = mimetypes.guess_type(path)[0]
                        if mtype in images:
                            image = images[mtype]
                        else:
                            image=icons.icons.get_mime_image(mtype)
                        
                        i = FileTreeItem(path, fsi, image=image)
                        self.__fileview.add_item(i, get_root())
                for childpath in childnodes:
                    childiter = self.__fileview.model.get_iter(childpath)
                    self.__fileview.model.remove(childiter)

            t = threading.Thread(target=listdir)
            t.run()
            


            #self.emit('directory-changed', directory)


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
        print self.__fileview.selected.value.path
        filepath = self.__fileview.selected.key
        if filepath:
            treepath = self.__fileview.selected_path
            if os.path.isdir(filepath):
                if self.__fileview.view.row_expanded(treepath):
                #self.display(filepath, self.__fileview.selected_iter)
                    self.__fileview.view.collapse_row(treepath)
                else:
                    self.__fileview.view.expand_row(treepath, False)
            else:
                print filepath
                self.emit('file-activated', filepath)

    def cb_file_rightclicked(self, view, fileitem, event):
        fsi = fileitem.value
        if fsi.directory:
            menu = self.boss.command('contexts', 'get-menu',
                                     contextname='directory',
                                     globaldict={'directory':fsi.path})
        else:
            menu = self.boss.command('contexts', 'get-menu',
                                     contextname='file',
                                     globaldict={'filename':fsi.path})
        menu.popup(None, None, None, event.button, event.time)
       


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

    def toolbar_action_new(self):
        if self.__currentdirectory is not None:
            self.boss.command('newfile', 'create-interactive',
                              directory=self.__currentdirectory)
        

gobject.type_register(FileBrowser)

if __name__ == '__main__':
    w = gtk.Window()
    f = FileBrowser(None)
    w.add(f)
    w.show_all()
    f.display('/home/ali')
    gtk.main()
        
