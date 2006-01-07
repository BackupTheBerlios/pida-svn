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
import pida.pidagtk.contextwidgets as contextwidgets

import pida.core.registry as registry
import pida.core.service as service
types = service.types
defs = service.definitions

import gtk
import os
import gobject
import os.path

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

    SORT_BY = 'name'

    markup_format_string = ('<b>%(name)s</b> ('
                            '<span color="#0000c0">%(vcs_name)s</span>'
                            ')\n%(source_directory)s')

    def set_projects(self, projects):
        self.clear()
        for project in projects:
            # remove
            project.key = project.name
            self.add_item(project, key=project.name)


class project_view(contentview.content_view):
    SHORT_TITLE = 'Projects'
    ICON_NAME = 'project'
    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = False

    def init(self):
        self.__toolbar = contextwidgets.context_toolbar()
        self.widget.pack_start(self.__toolbar, expand=False)
        self.__projectlist = ProjectTree()
        self.widget.pack_start(self.__projectlist)
        self.__projectlist.set_property('markup-format-string',
            self.__projectlist.markup_format_string)
        self.__projectlist.connect('clicked',
            self.service.cb_plugin_view_project_clicked)
        self.__projectlist.connect('right-clicked',
            self.cb_list_right_clicked)

    def set_projects(self, *args):
        self.__projectlist.set_projects(self.service.projects)

    def get_selected(self):
        return self.__projectlist.selected

    def set_contexts(self, contexts):
        self.__toolbar.set_contexts(contexts)

    def cb_list_right_clicked(self, treeview, item, event):
        globaldict = {'directory': item.value.source_directory,
                      'project': item.value}
        menu = gtk.Menu()
        for title, context in [('Directory', 'directory'),
                        ('Source code', 'project_directory'),
                        ('Project', 'project')]:
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

class ProjectManager(service.service):
    """Project Management"""

    # view definitions

    plugin_view_type = project_view

    single_view_type = configview.config_view
    single_view_book = 'ext'

    class default(defs.project_type):
        project_type_name = 'default'
        class general(defs.optiongroup):
            """General options for Python projects"""
            class source_directory(defs.option):
                """The directory containing source code."""
                rtype = types.directory
                default = os.path.expanduser('~')
   
    # life cycle
 
    def init(self):
        self.__current_project = None
        self.__history = []
        self.__history_file = os.path.join(self.boss.pida_home,
            'projects', 'projectlist.conf')
        if not os.path.exists(self.__history_file):
            self.__write_history()

    def reset(self):
        pass

    def stop(self):
        pass

    # private interface

    def __read_history(self):
        self.__history = []
        f = open(self.__history_file, 'r')
        for filename in f:
            self.__history.append(filename.strip())
        f.close()

    def __write_history(self):
        f = open(self.__history_file, 'w')
        for filename in self.__history:
            f.write('%s\n' % filename)
        f.close()

    def __update(self):
        self.__read_history()
        self.__load_projects()
        self.plugin_view.set_projects()

    def __load_projects(self):
        self.__projects = []
        for filename in self.__history:
            project = self.boss.call_command('projecttypes',
                        'load_project', project_file_name=filename)
            if project is not None:
                self.__projects.append(project)
             

    def __launch_editor(self, projects=None, current_project=None):
        if projects is None:
            projects = self.projects
        view = self.create_single_view()
        view.connect('data-changed', self.cb_data_changed)
        view.set_registries([(p.name, p.options) for p in projects])
        if current_project is not None:
            self.single_view.show_page(current_project.name)

    def __current_project_changed(self, project):
        if project is not self.__current_project:
            if self.__current_project is not None:
                self.__current_project.project_type.action_group.\
                    set_visible(False)
            self.__current_project = project
            self.__current_project.project_type.action_group.set_visible(True)
            self.boss.call_command('window', 'update_action_groups')
            directory = project.source_directory
            def browse():
                if directory is not None:
                    self.boss.call_command('filemanager', 'browse',
                                       directory=directory)
            gobject.timeout_add(100, browse)

    # external interface
   
    def get_projects(self):
        for project in self.__projects:
            yield project
    projects = property(get_projects)

    # bindings
    
    def bnd_projecttypes_project_type_registered(self):
        self.__update()

    #commands

    def cmd_edit(self, projects=None, current_project=None):
        if current_project is None:
            current_project = self.__current_project
        self.__launch_editor(projects, current_project)

    def cmd_add_project(self, project_file):
        self.__history.append(project_file)
        self.__history = list(set(self.__history))
        self.__write_history()
        self.__update()

    def cmd_remove_project(self, project):
        self.__history.remove(project.project_filename)
        self.__write_history()
        self.__update()

    def cmd_get_current_project(self):
        return self.__current_project

    # Actions

    def act_new_project(self, action):
        """Create a new project."""
        self.boss.call_command('projectcreator', 'create_interactive')

    def act_properties(self, action):
        """See or edit the properties for this project."""
        self.call('edit')

    def act_add_project(self, action):
        fdialog = gtk.FileChooserDialog('Please select the project file',
                                 parent=self.boss.get_main_window(),
                                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                 buttons=(gtk.STOCK_OK,
                                          gtk.RESPONSE_ACCEPT,
                                          gtk.STOCK_CANCEL,
                                          gtk.RESPONSE_REJECT))
        def response(dialog, response):
            if response == gtk.RESPONSE_ACCEPT:
                self.call('add_project', project_file=dialog.get_filename())
            dialog.destroy()
        fdialog.connect('response', response)
        fdialog.run()

    def act_commit_project(self, action):
        """Commit the current project to version control"""
        directory = self.__current_project.source_directory
        self.boss.call_command('versioncontrol', 'commit',
                               directory=directory)
        pass

    def act_get_project_statuses(self, action):
        pass

    def act_update_project(self, action):
        """Update the current project from version control"""
        directory = self.__current_project.source_directory
        self.boss.call_command('versioncontrol', 'update',
                               directory=directory)

    def act_remove_project_from_workbench(self, action):
        self.call('remove_project', project=self.__current_project)

    # view callbacks

    def cb_plugin_view_project_clicked(self, tree, item):
        self.__current_project_changed(item.value)

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

    # ui definition

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                </menu>
                <menu name="base_project" action="base_project_menu">
                <menuitem name="newproj" action="projectmanager+new_project" />
                <menuitem name="addproj" action="projectmanager+add_project" />
                <separator />
                <menuitem name="remproj"
                    action="projectmanager+remove_project_from_workbench" />
                <separator />
                <menuitem name="propproj" action="projectmanager+properties" />
                <separator />
                <separator />
                <menuitem name="statproj"
                    action="projectmanager+get_project_statuses" />
                <menuitem name="upproj" action="projectmanager+update_project" />
                <menuitem name="comproj" action="projectmanager+commit_project" />
                <separator />
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
            </placeholder>
            <placeholder name="SaveFileToolbar">
            </placeholder>
            <placeholder name="EditToolbar">
            </placeholder>
            <placeholder name="ProjectToolbar">
            </placeholder>
            <placeholder name="VcToolbar">
                <separator />
                <toolitem name="upproj" action="projectmanager+update_project" />
                <toolitem name="comproj" action="projectmanager+commit_project" />
                <separator />
            </placeholder>
            </toolbar>
        """


Service = ProjectManager


