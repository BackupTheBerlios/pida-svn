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

import pida.core.plugin as plugin
import pida.core.registry as registry
import pida.pidagtk.tree as tree
import pida.pidagtk.listedtab as listedtab
import pida.pidagtk.contentbook as contentbook
import gtk
import os
class Project(object):

    name = None
    directory = None
    environment = None
    vcs = None

class ProjectTreeItem(tree.TreeItem):

    def __get_markup(self):
        directory = self.value.directory
        vcs = self.value.vcs
        wd = directory
        wd = wd.replace(os.path.expanduser('~'), '~')
        b = ('<span size="small"><b>%s</b> ('
            '<span foreground="#0000c0">%s</span>)\n'
            '%s</span>') % (self.value.name, vcs, wd)
        return b
    markup = property(__get_markup)

class ProjectTree(tree.Tree):
    EDIT_BUTTONS = True
    def set_projects(self, registry):
        for project in registry:
            item = ProjectTreeItem(project.name, project)
            self.add_item(item)

REGISTRY_SCHEMA = [('directory', 'the directory', '/', registry.Directory),
                   ('environment', 'the environment', '', registry.RegistryItem)]

class ProjectManager(plugin.Plugin):
    """Project Management"""
    NAME = 'projectmanager'
    OPTIONS = [('filename', 'The project file.',
                '/home/ali/.pida2/conf/projects.conf', registry.File)]
    ICON = 'project'

    def init(self):
        self.__registry = registry.Registry()
        self.__filename = None

    def populate(self):
        self.__projectlist = ProjectTree()
        self.view.pack_start(self.__projectlist)
        self.__projectlist.connect('new-item', self.cb_new_project)
        self.__projectlist.connect('delete-item', self.cb_delete_project)
        self.__projectlist.connect('clicked', self.cb_project_clicked)

    def cb_project_clicked(self, tree, item):
        directory = item.value.directory
        self.boss.command('filemanager', 'browse', directory=directory)

    def cb_new_project(self, treeview):
        self.__project_editor = ProjectEditor(self.__registry)
        self.__content = contentbook.ContentView()
        self.__content.pack_start(self.__project_editor)
        self.boss.command('viewbook', 'add-page',
                           contentview=self.__content)

    def cb_edit_project(self):
        pass

    def cb_delete_project(self, treeview, treeitem):
        if treeitem is not None:
            print treeitem.value

    def reset(self):
        if self.registry_filename != self.__filename:
            self.__registry.load_file_with_schema(
                self.registry_filename, REGISTRY_SCHEMA)
            self.__filename = self.registry_filename
            self.__projectlist.set_projects(self.__adapt_registry())
    
    def __adapt_registry(self):
        for group in self.__registry.iter_groups():
            p = Project()
            p.name = group._name
            p.directory = group.get('directory').value()
            p.vcs = self.boss.command('versioncontrol',
                        'get-vcs-for-directory', directory=p.directory)
            p.environment = group.get('environment').value()
            yield p

    def __get_registry_filename(self):
        return self.options.get('filename').value()
    registry_filename = property(__get_registry_filename)
        

class ProjectEditor(listedtab.ListedTab):
    pass

    

Plugin = ProjectManager


