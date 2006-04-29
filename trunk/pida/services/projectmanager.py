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
import pida.pidagtk.contentview as contentview
from pida.model import model, views, persistency
import pida.core.registry as registry
import pida.core.service as service
import pida.core.actions as actions
import pida.core.project as project
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

class ProjectTree(views.TreeObserver):

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
        self.view.set_expander_column(self.view.get_column(1))


class project_view(contentview.content_view):
    SHORT_TITLE = 'Projects'
    LONG_TITLE = 'List of projects'
    ICON_NAME = 'project'
    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = False

    def init(self):
        self.proj_list = self.service.proj_group.create_multi_observer(
                                                    ProjectTree)
        self.proj_list.connect('clicked',
            self.service.cb_plugin_view_project_clicked)
        self.proj_list.connect('double-clicked',
            self.service.cb_plugin_view_project_double_clicked)
        self.proj_list.connect('right-clicked',
            self.cb_list_right_clicked)
        self.widget.pack_start(self.proj_list)


    def get_selected(self):
        return self.proj_list.selected

    def cb_list_right_clicked(self, treeview, item, event):
        if item is None:
            menu = gtk.Menu()
            for act in ['projectmanager+new_project',
                        'projectmanager+add_project']:
                action = self.service.action_group.get_action(act)
                mi = action.create_menu_item()
                menu.add(mi)
        else:
            menu = self.service.boss.call_command('contexts',
                'get_context_menu', ctxname='directory',
                ctxargs=[item.value.source__directory])
            menu.add(gtk.SeparatorMenuItem())
            for act in ['projectmanager+properties',
                        'projectmanager+remove_project_from_workbench']:
                action = self.service.action_group.get_action(act)
                mi = action.create_menu_item()
                menu.add(mi)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)

    def get_model(self):
        return self.proj_list.model

    def set_selected(self, key):
        self.__projectlist.set_selected(key)
    
    def get_selected_iter(self):
        return self.__projectlist.selected_iter


class ProjectEditor(contentview.content_view):

    def init(self):
        mg = self.service.proj_group
        self.tv = mg.create_multi_observer(views.TreeObserver)
        self.pp = mg.create_single_observer(views.PropertyPage)
        b = gtk.HPaned()
        b.pack1(self.tv)
        b.pack2(self.pp)
        b.set_position(200)
        self.widget.pack_start(b)


class ProjectManager(service.service):
    """Project Management"""

    # view definitions

    class ProjectView(defs.View):
        view_type = project_view
        book_name = 'content'

    class ProjectEditor(defs.View):
        view_type = ProjectEditor
        book_name = 'edit'

    # life cycle
    def init(self):
        self.__current_project = None
        self.__history = []
        self.__history_file = os.path.join(self.boss.pida_home,
            'projects', 'projectlist.conf')
        self.__last_file = os.path.join(self.boss.pida_home,
            'projects', 'projectlast.conf')
        if not os.path.exists(self.__history_file):
            self.__write_history()
        self.__started = False
        self.__init_model()
        self.__read_history()
        self.create_view('ProjectView')
        self.__init_project_toolbar()
        self._editview = None

    def __init_model(self):
        def _act(item):
            self.__current_project_activated()
        self.proj_group = model.ModelGroup(_act)
        self.ini_watch = self.proj_group.create_single_observer(
            persistency.IniFileObserver)
        self.act_watch = self.proj_group.create_single_observer(
            views.ActionSensitivityObserver)
        act = self.action_group.get_action('projectmanager+execute_project')
        self.act_watch.add_widget(act, 'execution__uses')
        #act.set_sensitive(self.__current_project.execution__uses)

    def __init_project_toolbar(self):
        tb = self.boss.call_command('window', 'get_ui_widget',
                               path='/toolbar')
        ph = self.boss.call_command('window', 'get_ui_widget',
                               path='/toolbar/VcToolbar')
        i = tb.get_item_index(ph)
        ti = gtk.ToolItem()
        tb.insert(ti, i)
        tbox = gtk.HBox(spacing=6)
        ti.add(tbox)
        self.__projects_combo = self.proj_group.create_multi_observer(
            views.ComboObserver)
        tbox.pack_start(self.__projects_combo)

    def reset(self):
        if not self.__started:
            self.__started = True
            if os.path.exists(self.__last_file):
                f = open(self.__last_file, 'r')
                name = f.read().strip()
                f.close()
                for proj in self.proj_group:
                    if proj.general__name == name:
                        self.proj_group.set_current(proj)
                        self.__current_project_activated()

    def stop(self):
        if self.__current_project is not None:
            f = open(self.__last_file, 'w')
            f.write(self.__current_project.general__name)
            f.close()

    # private interface

    def __set_toolbar(self):
        self.__projects_combo.set_model(self.plugin_view.get_model())
        self.__projects_combo.set_property('text-column', 2)
        entry = self.__projects_combo.get_children()[0]
        entry.set_editable(False)

    def __read_history(self):
        f = open(self.__history_file, 'r')
        hist = set()
        for filename in f:
            filename = filename.strip()
            if os.path.exists(filename):
                hist.add(filename)
        f.close()
        for filename in hist:
            p = project.Project()
            persistency.load_model_from_ini(filename, p)
            p.__model_ini_filename__ = filename
            self.proj_group.add_model(p)
        self.__write_history()

    def __write_history(self):
        f = open(self.__history_file, 'w')
        for proj in set(self.proj_group):
            f.write('%s\n' % proj.general__filename)
        f.close()

    def __launch_editor(self, projects=None, current_project=None):
        if self._editview is None:
            self._editview = self.create_view('ProjectEditor')
            self.show_view(view=self._editview)
        self._editview.raise_page()

    def __current_project_changed(self, project):
        if project is not self.__current_project:
            self.__current_project = project

    def __current_project_activated(self):
        if self.__current_project is not None:
            directory = self.__current_project.general__browse_directory
            if directory is not None:
                self.boss.call_command('filemanager', 'browse',
                                        directory=directory)

    # external interface
    def get_projects(self):
        for project in self.__projects:
            yield project
    projects = property(get_projects)

    # bidings
    def bnd_filemanager_directory_changed(self, directory):
        if self.__current_project is not None:
            self.__current_project.general__browse_directory = directory

    #commands

    def cmd_edit(self, projects=None, current_project=None):
        if current_project is None:
            current_project = self.__current_project
        self.__launch_editor(projects, current_project)

    def cmd_create_project(self):
        chooser = gtk.FileChooserDialog("Save Project File",
                        self.boss.get_main_window(),
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                        gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        chooser.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        filt = gtk.FileFilter()
        filt.add_pattern('*.pida')
        chooser.set_filter(filt)
        try:
            chooser.set_do_overwrite_confirmation(True)
        except AttributeError:
            pass
        def response(dialog, resp):
            chooser.hide()
            fn = dialog.get_filename()
            chooser.destroy()
            if resp != gtk.RESPONSE_ACCEPT:
                return
            p = project.Project()
            if not fn.endswith('.pida'):
                fn = '%s.pida' % fn
            p.__model_ini_filename__ = fn
            self.proj_group.add_model(p)
            p.general__name = os.path.basename(fn).split('.')[0]
            self.proj_group.set_current(p)
            self.__write_history()
            self.cmd_edit()
        chooser.connect('response', response)
        chooser.show_all()


    def cmd_add_project(self, project_file):
        p = project.Project()
        m = persistency.load_model_from_ini(project_file, p)
        m.__model_ini_filename__ = project_file
        self.proj_group.add_model(m)
        self.__write_history()
        #self.__update()

    def cmd_remove_project(self, project):
        self.proj_group.remove_model(project)
        self.__write_history()

    def cmd_get_current_project(self):
        return self.__current_project

    def cmd_get_projects(self):
        return self.projects

    def cmd_get_project_for_file(self, filename):
        if filename is None:
            return None
        for project in self.projects:
            if project.source__directory in filename:
                return project
        return None

    # Actions

    @actions.action(stock_id='gtk-new')
    def act_new_project(self, action):
        """Create a new project."""
        self.cmd_create_project()

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

    @actions.action(stock_id='vcs_commit',
        default_accel='<Shift><Control>c')
    def act_commit_project(self, action):
        """Commit the current project to version control"""
        if self.__current_project is not None:
            directory = self.__current_project.source_directory
            self.boss.call_command('versioncontrol', 'commit',
                                   directory=directory)

    @actions.action(stock_id='vcs_update',
                    default_accel='<Shift><Control>u')
    def act_update_project(self, action):
        """Update the current project from version control"""
        if self.__current_project is not None:
            directory = self.__current_project.source_directory
            self.boss.call_command('versioncontrol', 'update',
                                directory=directory)

    @actions.action(stock_id='gtk-project',
                    default_accel='<Shift><Control>x')
    def act_execute_project(self, action):
        com = self.__current_project.execution__command
        """Execute the current project."""
        shell_cmd = 'sh'
        if com:
            self.boss.call_command('terminal', 'execute',
                command_args=[shell_cmd, '-c', com], icon_name='run')
        else:
            self.log.info('project has not set an executable')

    @actions.action(stock_id='gtk-remove')
    def act_remove_project_from_workbench(self, action):
        self.call('remove_project', project=self.__current_project)

    # view callbacks
    def cb_plugin_view_project_clicked(self, tree, item):
        self.__current_project_changed(item.value)

    def cb_combo_changed(self, cmb):
        ite = cmb.get_active_iter()
        project = cmb.get_model().get_value(ite, 1).value
        self.plugin_view.set_selected(project.name)
        self.__current_project_activated()

    def cb_plugin_view_project_double_clicked(self, tree, item):
        self.__current_project_activated()

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

    def view_closed(self, view):
        self.proj_group.remove_observer(view.pp)
        self.proj_group.remove_observer(view.tv)
        self._editview = None
    # ui definition

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                </menu>
                <menu name="base_project" action="base_project_menu">
                <placeholder name="ProjectMain">
                <menuitem name="newproj" action="projectmanager+new_project" />
                <menuitem name="addproj" action="projectmanager+add_project" />
                <separator />
                <menuitem name="remproj"
                    action="projectmanager+remove_project_from_workbench" />
                <separator />
                <menuitem name="propproj" action="projectmanager+properties" />
                <menuitem name="upproj" action="projectmanager+update_project" />
                <menuitem name="comproj" action="projectmanager+commit_project" />
                <separator />
                </placeholder>
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
                <toolitem name="exproj" action="projectmanager+execute_project" />
            </placeholder>
            <placeholder name="VcToolbar">
                <toolitem name="upproj" action="projectmanager+update_project" />
                <toolitem name="comproj" action="projectmanager+commit_project" />
                <separator />
            </placeholder>
            </toolbar>
        """

    def get_plugin_view(self):
        return self.get_first_view('ProjectView')
    plugin_view = property(get_plugin_view)


Service = ProjectManager


