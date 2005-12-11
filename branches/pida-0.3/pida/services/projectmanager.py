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
import pida.pidagtk.configview as configview
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

    markup_format_string = ('<b>%(name)s</b>')

    def set_projects(self, projects):
        self.clear()
        for project in projects:
            self.add_item(project, project.name)

#REGISTRY_SCHEMA = [('directory', 'the directory', '/', registry.Directory),
#                   ('environment', 'the environment', '', registry.RegistryItem)]


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

    single_view_type = configview.config_view
    single_view_book = 'view'
    
    def init(self):
        self.__projectsdir = os.path.join(self.boss.pida_home, 'projects')

    def __update(self):
        self.__load_projects()
        self.plugin_view.set_projects()

    def bnd_projectcreator_project_created(self):
        self.__update()

    def bnd_projecttypes_project_type_registered(self):
        self.__update()

    def cb_plugin_view_project_clicked(self, tree, item):
        gen_opts = item.value.options.get('general')
        if gen_opts is not None:
            diropt = gen_opts.get('source_directory')
            if diropt is not None:
                source_dir = diropt.value
                self.boss.call_command('filemanager', 'browse',
                                       directory=source_dir)
                
        #directory = item.value.directory
        #self.__current_directory = directory
        #for child in self.view.bar_area.get_children():
        #    self.plugin_view.bar_area.remove(child)
        #    child.destroy()
        #tb = self.boss.command('contexts', 'get-toolbar',
        #                       contextname='directory',
        #                       globaldict={'directory': directory})
        #self.plugin_view.bar_area.pack_start(tb, expand=False)

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

    def cb_data_changed(self, configview):
        self.__update()

    def __load_projects(self):
        self.__projects = []
        for projecttype in os.listdir(self.__projectsdir):
            typedir = os.path.join(self.__projectsdir, projecttype)
            # check if type exists
            for filename in os.listdir(typedir):
                filepath = os.path.join(typedir, filename)
                project = self.boss.call_command('projecttypes',
                        'load_project', project_type_name=projecttype,
                        project_file_name=filepath)
                if project is not None:
                    self.__projects.append(project)
                
    def get_projects(self):
        for project in self.__projects:
            yield project
    projects = property(get_projects)

    def cmd_edit(self):
        view = self.create_single_view()
        view.connect('data-changed', self.cb_data_changed)
        view.set_registries([(p.name, p.options) for p in self.projects])

    def act_new_project(self, action):
        """Create a new project."""
        self.boss.call_command('projectcreator', 'create_interactive')

    def act_properties(self, action):
        """See or edit the properties for this project."""
        self.call('edit')

    def act_commit_project(self, action):
        pass

    def act_get_project_statuses(self, action):
        pass

    def act_update_project(self, action):
        pass

    

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                </menu>
                <menu name="base_project" action="base_project_menu">
                <menuitem name="newproj" action="projectmanager+new_project" />
                <separator />
                <menuitem name="statproj"
                    action="projectmanager+get_project_statuses" />
                <menuitem name="upproj" action="projectmanager+update_project" />
                <menuitem name="comproj" action="projectmanager+commit_project" />
                <separator />
                <menuitem name="propproj" action="projectmanager+properties" />
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                <toolbar>
                <separator />
                <toolitem name="tstatproj"
                    action="projectmanager+get_project_statuses" />
                <toolitem name="tupproj" action="projectmanager+update_project" />
                <toolitem name="tcomproj"
                    action="projectmanager+commit_project" />
                <separator />
                </toolbar>
        """


Service = ProjectManager


