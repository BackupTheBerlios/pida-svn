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

import pida.pidagtk.tree as tree
import pida.pidagtk.dataview as dataview
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.contentview as contentview

import pida.core.service as service
types = service.types
defs = service.definitions

import gtk
import os
import os.path

PROJECT_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "conf", "projects.conf")

class Project(object):

    name = None
    directory = None
    environment = None
    vcs = None
    vcsname = None

class ProjectTreeItem(tree.TreeItem):

    def __get_markup(self):
        directory = self.value.directory
        vcs = self.value.vcsname
        wd = directory
        wd = wd.replace(os.path.expanduser('~'), '~')
        b = ('<span><b>%s</b> ('
            '<span foreground="#0000c0">%s</span>)\n'
            '%s</span>') % (self.value.name, vcs, wd)
        return b
    markup = property(__get_markup)

class ProjectTree(tree.Tree):

    EDIT_BUTTONS = True
    SORT_BY = 'name'

    markup_format_string = ('<b>%(name)s</b> '
                            '<span color="#0000c0">(%(vcsname)s)</span>\n'
                            '%(directory)s')

    def set_projects(self, projects):
        self.clear()
        for project in projects:
            self.add_item(project, project.key)

#REGISTRY_SCHEMA = [('directory', 'the directory', '/', registry.Directory),
#                   ('environment', 'the environment', '', registry.RegistryItem)]


class ProjectEditorView(dataview.data_view):

    LONG_TITLE = 'pIDA project editor'
    SHORT_TITLE = 'Projects'
    pass

class project_view(contentview.content_view):
    SHORT_TITLE = 'Projects'
    ICON_NAME = 'project'
    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = False

    def init(self):
        self.__projectlist = ProjectTree()
        self.__projectlist.set_property('markup-format-string',
            self.__projectlist.markup_format_string)
        self.widget.pack_start(self.__projectlist)
        self.__projectlist.connect('new-item',
            self.service.cb_plugin_view_new_clicked)
        self.__projectlist.connect('edit-item',
            self.service.cb_plugin_view_edit_clicked)
        self.__projectlist.connect('delete-item',
            self.service.cb_plugin_view_delete_clicked)
        self.__projectlist.connect('clicked',
            self.service.cb_plugin_view_project_clicked)

    def set_projects(self, *args):
        self.__projectlist.set_projects(self.service.projects)

    def get_selected(self):
        return self.__projectlist.selected


class ProjectManager(service.service):
    """Project Management"""

    plugin_view_type = project_view
    
    class project_data(defs.database):
        """A database to store fruits.""" 
        DATA_VIEW = ProjectEditorView
        class name(defs.field):
            rtype = types.string
            default = ''
        class directory(defs.field):
            rtype = types.directory
            default = os.path.expanduser('~')
        class environment(defs.field):
            rtype = types.string
            default = ''

    def init(self):
        self.plugin_view.set_projects()

    def cb_data_view_applied(self, dataname):
        self.plugin_view.set_projects()
        
    def cb_plugin_view_project_clicked(self, tree, item):
        directory = item.value.directory
        self.__current_directory = directory
        #for child in self.view.bar_area.get_children():
        #    self.plugin_view.bar_area.remove(child)
        #    child.destroy()
        #tb = self.boss.command('contexts', 'get-toolbar',
        #                       contextname='directory',
        #                       globaldict={'directory': directory})
        #self.plugin_view.bar_area.pack_start(tb, expand=False)
        self.boss.call_command('filemanager', 'browse', directory=directory)

    def cb_plugin_view_new_clicked(self, treeview):
        self.create_data_view('project_data')

    def cb_plugin_view_edit_clicked(self, treeview):
        self.create_editorview(self.__registry)
        self.display_editorpage(self.__projectlist.get_selected_key())

    def cb_plugin_view_delete_clicked(self, toolbar):
        treeitem = self.plugin_view.get_selected()
        if treeitem is not None:
            del self.databases['project_data'][treeitem.key]
            self.databases['project_data'].sync()
            self.cb_data_changed('project_data')

    def cb_editor_applied(self, view):
        self.__projectlist.set_projects(self.__adapt_registry())

    def cb_editor_newitem(self, view, name):
        newitem = self.__registry.add_group(name, '')
        for option in REGISTRY_SCHEMA:
            opt = newitem.add(*option)
            opt.setdefault()
        self.__registry.save()
        self.__projectlist.set_projects(self.__adapt_registry())
        self.editorview.tab.reset()
        self.editorview.tab.display_page(name)

    def reset(self):
        pass

    def cb_data_changed(self, dataname):
        self.plugin_view.set_projects()
    
    def adapt_registry(self):
        for key in self.databases['project_data']:
            project = self.databases['project_data'][key]
            project.name = key
            project.key = key
            #p.directory = group.get('directory').value()
            #p.vcs, p.vcsname = self.boss.command('versioncontrol',
            #            'get-vcs-for-directory', directory=p.directory)
            #p.environment = group.get('environment').value()
            project.vcs = project.vcsname = None
            yield project
    projects = property(adapt_registry)


    def cmd_edit(self):
        self.create_data_view('project_data')
        

    def act_new_project(self, action):
        """Create a new project."""
        self.call('edit')

    def act_properties(self, action):
        """See or edit the properties for this project."""
        self.call('edit')

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                </menu>
                <menu name="base_project" action="base_project_menu">
                <menuitem name="newproj" action="project+new_project" />
                <separator />
                <menuitem name="propproj" action="project+properties" />
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
        """


Service = ProjectManager


