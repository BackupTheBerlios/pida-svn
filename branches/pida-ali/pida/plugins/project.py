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
import os.path

PROJECT_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "conf", "projects.conf")

class Project(object):

    name = None
    directory = None
    environment = None
    vcs = None

class ProjectTreeItem(tree.TreeItem):

    def __get_markup(self):
        directory = self.value.directory
        vcs = self.value.vcsname
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

class ProjectEditorTree(tree.Tree):

    EDIT_BUTTONS = True

class ProjectEditor(listedtab.ListedTab):
    
    TREE = ProjectEditorTree

class ProjectEditorView(contentbook.TabView):

    TAB_VIEW = ProjectEditor


class ProjectManager(plugin.Plugin):
    """Project Management"""
    NAME = 'projectmanager'
    OPTIONS = [('filename', 'The project file.',
                PROJECT_CONF, registry.File)]
    ICON = 'project'

    BUTTONS = [('find', 'find', 'Search for text in this directory'),
               ('vcsup', 'vcs_update',
                'Update the version control for this directory'),
               ('vcscommit', 'vcs_commit',
                'Commit the directory to version control'),
               ('vcsstatus', 'vcs_diff',
                'Get the status for files in this project.')]

    EDITOR_VIEW = ProjectEditorView

    def init(self):
        self.__registry = registry.Registry()
        self.__filename = None
        self.__current_directory = None
        self.__project_editor = None

    def populate(self):
        self.__projectlist = ProjectTree()
        self.view.pack_start(self.__projectlist)
        self.__projectlist.connect('new-item', self.cb_new_project)
        self.__projectlist.connect('edit-item', self.cb_edit_project)
        self.__projectlist.connect('delete-item', self.cb_delete_project)
        self.__projectlist.connect('clicked', self.cb_project_clicked)

    def cb_project_clicked(self, tree, item):
        directory = item.value.directory
        self.__current_directory = directory
        self.boss.command('filemanager', 'browse', directory=directory)

    def cb_new_project(self, treeview):
        self.create_editorview(self.__registry)

    def cb_edit_project(self, treeview):
        self.create_editorview(self.__registry)
        self.display_editorpage(self.__projectlist.get_selected_key())

    def cb_delete_project(self, treeview, treeitem):
        if treeitem is not None:
            print treeitem.value

    def reset(self):
        if self.registry_filename != self.__filename:
            self.reload()

    def reload(self):
        self.__registry.load_file_with_schema(
            self.registry_filename, REGISTRY_SCHEMA)
        self.__filename = self.registry_filename
        self.__projectlist.set_projects(self.__adapt_registry())
    
    def __adapt_registry(self):
        for group in self.__registry.iter_groups():
            p = Project()
            p.name = group._name
            p.directory = group.get('directory').value()
            p.vcs, p.vcsname = self.boss.command('versioncontrol',
                        'get-vcs-for-directory', directory=p.directory)
            p.environment = group.get('environment').value()
            yield p

    def __get_registry_filename(self):
        return self.options.get('filename').value()
    registry_filename = property(__get_registry_filename)

    def toolbar_action_find(self):
        if self.__current_directory is not None:
            self.boss.command('grepper', 'find-interactive',
                               directories=[self.__current_directory])
    
    def toolbar_action_vcsup(self):
        if self.__current_directory is not None:
            self.boss.command('versioncontrol', 'up',
                               directory=self.__current_directory)

    def toolbar_action_vcscommit(self):
        if self.__current_directory is not None:
            self.boss.command('versioncontrol', 'commit-directory',
                               directory=self.__current_directory)

    def toolbar_action_vcsstatus(self):
        if self.__current_directory is not None:
            self.boss.command('versioncontrol', 'status',
                               directory=self.__current_directory)

        
    

Plugin = ProjectManager


