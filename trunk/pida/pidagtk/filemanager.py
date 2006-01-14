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
import toolbar
import gobject
import threading
import contentview
import mimetypes
import contextwidgets

def shorten_home_name(directory):
    return directory.replace(os.path.expanduser('~'), '~')

import pida.utils.gforklet as gforklet

DIR_ICON = icons.icons.get_image('filemanager')

class FileTree(tree.IconTree):

    SORT_LIST = ['isdir', 'name']

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
        self.set_property('markup-format-string', '%(markup)s')
        self.__fm = fm
        self.view.connect('row-expanded', self.cb_row_expanded)

    def cb_row_expanded(self, view, titer, path):
        item = self.get(titer, 1).value
        self.__fm.display(item.path, rootpath=path)
        return True

class FileSystemItem(object):

    def __init__(self, path):
        self.path = path
        self.key = path
        self.name = os.path.basename(path)
        if os.path.isdir(path):
            self.isdir = -1
        else:
            self.isdir = 1

    def __get_markup(self):
        color = '#000000'
        if self.isdir < 0:
            color = '#0000c0'
        return ('<tt><span color="%s"><span color="#600060"><b>%s'
                '</b>  </span>%s</span></tt>' %
                (color, self.status, self.name))
    markup = property(__get_markup)

    def get_pixbuf(self):
        if self.isdir < 0:
            return DIR_ICON.get_pixbuf()
        else:
            return None
    
    pixbuf = property(get_pixbuf)

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
        tb = gtk.HBox()
        self.widget.pack_start(tb, expand=False)
        own_tb = toolbar.Toolbar()
        own_tb.connect('clicked', self.cb_toolbar_clicked)
        own_tb.add_button('project_root', 'project',
                          'Browse the source directory of the current project')
        own_tb.add_button('refresh', 'refresh',
                          'Refresh the current directory')
        tb.pack_start(own_tb, expand=False)
        self.__toolbar = contextwidgets.context_toolbar()
        tb.pack_start(self.__toolbar, expand=False)
        #hbox = gtk.HPaned()
        #self.widget.pack_start(hbox)
        #sw = gtk.ScrolledWindow()
        #sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #hbox.pack2(sw)
        self.__fileview = FileTree(self)
        self.widget.pack_start(self.__fileview)
        self.__fileview.connect('double-clicked', self.cb_file_activated)
        self.__fileview.connect('right-clicked', self.cb_file_rightclicked)
        self.__currentdirectory = None
        self.t = None

    def display(self, directory, rootpath=None, statuses=[], glob='*', hidden=True):
        def _display():
            self.__fileview.clear()
            self.set_long_title(shorten_home_name(directory))
            self.__currentdirectory = directory
            globaldict = {'directory':directory}
            try:
                contexts = self.service.boss.call_command('contexts',
                                                            'get_contexts',
                                                contextname='directory',
                                                globaldict=globaldict)
                self.__toolbar.set_contexts(contexts)
            except self.service.boss.ServiceNotFoundError:
                pass

            SMAP = {0: 'i', 1:'?', 2:' ', 7: 'M', 6: 'A', 8: 'C', 9:'D'}
            
            statuses = self.service.boss.call_command('versioncontrol',
                    'get_statuses', directory=directory)
            files = [] 
            if statuses is None:
                def gen():
                    for filename in os.listdir(directory):
                        path = os.path.join(directory, filename)
                        fsi = FileSystemItem(path)
                        fsi.status = ' '
                        icon = None
                        #self.__fileview.add_item(fsi)
                        yield fsi
            else:
                def gen():
                    for s in statuses[::-1]:
                        fsi = FileSystemItem(s.path)
                        try:
                            fsi.status = SMAP[s.state]
                        except KeyError:
                            fsi.status = '%s %s' % (s.state, s.states[s.state])
                        yield fsi
                        #self.__fileview.add_item(fsi)
            gforklet.fork_generator(gen, [], self.__fileview.add_item)
            self.__fileview.show_all()

        if os.path.isdir(directory):
            _display()
        #    self.t = threading.Thread(target=_display)
        #    self.t.run()


            #self.emit('directory-changed', directory)


    def Go_up(self):
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
        filepath = self.__fileview.selected.key
        if filepath:
            treepath = self.__fileview.selected_path
            if os.path.isdir(filepath):
                #if self.__fileview.view.row_expanded(treepath):
                self.display(filepath, self.__fileview.selected_iter)
                #    self.__fileview.view.collapse_row(treepath)
                #else:
                #    self.__fileview.view.expand_row(treepath, False)
            else:
                self.emit('file-activated', filepath)

    def cb_file_rightclicked(self, view, fileitem, event):
        fsi = fileitem.value
        print fsi.isdir
        if os.path.isdir(fsi.path):
            self.__popup_dir(fsi.path, event)
        else:
            self.__popup_file(fsi.path, event)

    def __popup_file(self, path, event):

        globaldict = {'filename': path}
        menu = gtk.Menu()
        for title, context in [('Version control', 'file_vc'),
                        ('Parent directory', 'file_parent')]:
            mroot = gtk.MenuItem(label=title)
            menu.add(mroot)
            contexts = self.service.boss.call_command('contexts',
                                     'get_contexts',
                                     contextname=context,
                                     globaldict=globaldict
                                     )
            cmenu = contextwidgets.get_menu(contexts)
            mroot.set_submenu(cmenu)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)
       

    def __popup_dir(self, path, event):

        globaldict = {'directory': path}
        menu = gtk.Menu()
        for title, context in [('Directory', 'directory'),
                        ('Source code', 'project_directory')]:
            mroot = gtk.MenuItem(label=title)
            menu.add(mroot)
            contexts = self.service.boss.call_command('contexts',
                                     'get_contexts',
                                     contextname=context,
                                     globaldict=globaldict
                                     )
            cmenu = contextwidgets.get_menu(contexts)
            mroot.set_submenu(cmenu)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)


    def cb_dir_activated(self, tree, item):
        print item.key
        self.display(item.key)

    def cb_toolbar_clicked(self, toolbar, name):
        funcname = 'toolbar_action_%s' % name
        if hasattr(self, funcname):
            func = getattr(self, funcname)
            func()

    def toolbar_action_project_root(self):
        project = self.service.boss.call_command('projectmanager',
                                         'get_current_project')
        if project is not None:
            project_root = project.source_directory
            self.service.call('browse', directory=project_root)
        else:
            self.service.log.info('there is no project to go to its root')

    def toolbar_action_refresh(self):
        self.service.boss.call_command('versioncontrol',
            'forget_directory', directory=self.__currentdirectory)
        self.display(self.__currentdirectory)

    def get_directory(self):
        return self.__currentdirectory
    directory = property(get_directory)
        

gobject.type_register(FileBrowser)

if __name__ == '__main__':
    w = gtk.Window()
    f = FileBrowser(None)
    w.add(f)
    w.show_all()
    f.display('/home/ali')
    gtk.main()
        
