# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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
import os.path

import gtk

import pida.core.service as service
import pida.core.base as base

defs = service.definitions
types = service.types

import pida.pidagtk.gladeview as gladeview
import pida.core.actions as actions

class Contexts(service.service):

    def init(self):
        self.__defaults = {}
        self.__defaults['file_vc'] = file_versioncontrol_context()
        self.__defaults['directory'] = directory_context()
        self.__defaults['project_directory'] = project_directory_context()
        self.__defaults['project'] = project_context()
        self.__defaults['file_parent'] = file_parent_context()

    def cmd_get_contexts(self, contextname, globaldict):
        if contextname in self.__defaults:
            context = self.__defaults[contextname]
            contexts = context.get_contexts(globaldict)
        else:
            self.log.info('context %s does not exist', contextname)
            contexts = []
        return contexts

    def cmd_get_custom_toolbar(self, contextname, globaldict={}):
        group = self.__registry.get_group(contextname)
        if group is not None:
            tb = toolbar.Toolbar()
            scripts = group.get('scripts').value().split(',')
            scripts = [script.strip() for script in scripts]
            def clicked(clickedtb, name):
                self.boss.command('scripts', 'execute', scriptname=name,
                                  globaldict=globaldict)
            tb.connect('clicked', clicked)
            for script in scripts:
                tb.add_button(script, 'scripts',
                    'Click to execute script: %s' % script)
            return tb
    
    def __adapt_registry(self):
        for group in self.__registry.iter_groups():
            p = Context()
            p.name = group._name
            p.scripts = group.get('scripts').value().split(',')
            yield p

    def cmd_edit(self):
        self.create_data_view('contexts')

    def cmd_get_context_menu(self, ctxname, ctxargs):
        contexts = dict(file=FileContext, directory=DirectoryContext)
        ctx = contexts[ctxname](self, *ctxargs)
        return ctx.create_menu()


class default_context(base.pidacomponent):
    
    COMMANDS = []

    def get_contexts(self, globaldict):
        args = self.globals_modifier(globaldict)
        for name, icon, stext, ltext in self.COMMANDS:
            funcname = 'command_%s' % name
            if hasattr(self, funcname):
                func = getattr(self, funcname)
                yield name, icon, ltext, func, args

    def globals_modifier(globaldict):
        return globaldict
            

class file_parent_context(default_context):

    COMMANDS = [('filemanager', 'filemanager', 'File Manager',
                'Open a file manager in the parent directory of this file'),
                ('terminal', 'terminal', 'Terminal',
                'Open a terminal in the parent directory of this file')]

    def globals_modifier(self, globaldict):
        return globaldict['filename']

    def command_filemanager(self, filename):
        self.boss.call_command('filemanager', 'browse',
            directory=self.get_parent_directory(filename))

    def command_terminal(self, filename):
        self.boss.call_command('terminal', 'execute_shell',
        kwdict={'directory': self.get_parent_directory(filename)})

    def get_parent_directory(self, filename):
        directory = os.path.split(filename)[0]
        return directory

class file_versioncontrol_context(default_context):
    COMMANDS = [('vcs_diff', 'vcs_diff', 'VCS Statuses',
                 'Differences'),
                 ('vcs_add', 'vcs_add', 'VCS Add',
                 'Add'),
                 ('vcs_remove', 'vcs_remove', 'VCS Remove',
                 'Remove'),
                 ('vcs_revert', 'stock_undo', 'VCS revert',
                 'Revert')]

    def command_vcs_diff(self, filename):
        self.boss.call_command('versioncontrol', 'diff_file',
                               filename=filename)

    def command_vcs_add(self, filename):
        self.boss.call_command('versioncontrol', 'add_file',
                                filename=filename)

    def command_vcs_remove(self, filename):
        self.boss.call_command('versioncontrol', 'remove_file',
                                filename=filename)

    def command_vcs_revert(self, filename):
        self.boss.call_command('versioncontrol', 'revert_file',
                                filename=filename)

    def globals_modifier(self, globaldict):
        return globaldict['filename']
    


class directory_context(default_context):
    
    COMMANDS = [('up', 'up', 'Up',
                 'Browse the parent directoy'),
                ('new', 'new', 'New',
                 'Create a new file here'),
                ('dirnew', 'directory', 'New Directory',
                 'Create a new directory here'),
                ('terminal', 'terminal', 'Terminal',
                'Open a terminal here'),
                ('search', 'find', 'Search',
                'Search text in files here')]

    def globals_modifier(self, globaldict):
        return globaldict['directory']

    def command_filemanager(self, directory):
        self.boss.call_command('filemanager', 'browse', directory=directory)

    def command_find(self, directory):
        self.boss.call_command('grepper', 'find_interactive',
                           directories=[directory])

    def command_new(self, directory):
        self.boss.call_command('newfile', 'create_interactive',
                          directory=directory)
        gtk.idle_add(self._refresh_filemanager, directory)

    def command_dirnew(self, directory):
        self.boss.call_command('newfile', 'create_interactive',
                          directory=directory, mkdir=True)
        gtk.idle_add(self._refresh_filemanager, directory)

    def command_terminal(self, directory):
        self.boss.call_command('terminal', 'execute_shell',
                          kwdict={'directory': directory})

    def command_up(self, directory):
        if directory != '/':
            parent = os.path.split(directory)[0]
            self.boss.call_command('filemanager', 'browse', directory=parent)

    def command_search(self, directory):
        self.boss.call_command('grepper', 'find_interactive',
                               directories=[directory])

    def _refresh_filemanager(self, directory):
        curdir = self.boss.call_command('filemanager',
                                        'get_current_directory')
        if curdir == directory:
            self.boss.call_command('versioncontrol',
                'forget_directory', directory=directory)
            self.boss.call_command('filemanager', 'browse',
                                   directory=directory)


class project_directory_context(default_context):
    COMMANDS = [('vcs_diff', 'vcs_diff', 'VCS Statuses',
                 'Get the version statuses of this directory'),
                ('vcs_update', 'vcs_update', 'VCS Update',
                 'update this directory from version control.'),
                ('vcs_commit', 'vcs_commit', 'VCS Commit',
                 'commit this directory to version control.')]

    def command_vcs_diff(self, directory):
        self.boss.call_command('versioncontrol', 'statuses',
                               directory=directory)

    def command_vcs_commit(self, directory):
        self.boss.call_command('versioncontrol', 'commit',
                                directory=directory)

    def command_vcs_update(self, directory):
        self.boss.call_command('versioncontrol', 'update',
                                directory=directory)

    def globals_modifier(self, globaldict):
        return globaldict['directory']

class project_context(default_context):
    
    COMMANDS = [('properties', 'config', 'Project options',
                'Configure this project'),
                ('remove', 'delete', 'Remove project',
                'Remove project from workbench')]

    def globals_modifier(self, globaldict):
        return globaldict['project']

    def command_properties(self, project):
        self.boss.call_command('projectmanager', 'edit',
                               current_project=project)

    def command_remove(self, project):
        self.boss.call_command('projectmanager', 'remove_project',
                               project=project)

class ActionContext(actions.action_handler):
    
    type_name = 'context-actions'

    def init(self):
        self.__uim = gtk.UIManager()
        self.__uim.insert_action_group(self.action_group, 0)
        self.__uim.add_ui_from_string(self.get_menu_definition())

    def get_widget(self, path):
        return self.__uim.get_widget(path)

    def create_menu(self):
        menu = self.get_widget('/popup')
        menu.set_title(self.action_args[0])
        return menu

    def get_menu_definition(self):
        return "<popup />"

class VersionControlContextMixin(object):


    @actions.action(
        name='vcs_diff',
        stock_id='vcs_diff',
        label='Differences'
        )
    def act_vcs_diff(self, action, filename):
        self.boss.call_command('versioncontrol', 'diff_file',
                                filename=filename)

    @actions.action(
        name='vcs_add',
        stock_id='vcs_add',
        label='Add'
        )
    def act_vcs_add(self, action, filename):
        self.boss.call_command('versioncontrol', 'add_file',
                                filename=filename)

    @actions.action(
        name='vcs_revert',
        stock_id=gtk.STOCK_REVERT_TO_SAVED,
        label='Revert'
        )
    def act_vcs_revert(self, action, filename):
        self.boss.call_command('versioncontrol', 'revert_file',
                                filename=filename)

    @actions.action(
        name='vcs_update',
        stock_id='vcs_update',
        label='Update'
        )
    def act_vcs_update(self, action, filename):

        self.boss.call_command('versioncontrol', 'update',
                                directory=filename)


    @actions.action(
        name='vcs_commit',
        stock_id='vcs_commit',
        label='Commit'
        )
    def act_vcs_commit(self, action, filename):
        self.boss.call_command('versioncontrol', 'commit',
                                directory=filename)

    @actions.action(
        name='vcs_remove',
        stock_id='vcs_remove',
        label='Remove'
        )
    def act_vcs_remove(self, action, filename):
        self.boss.call_command('versioncontrol', 'remove_file',
                                filename=filename)

    @actions.action(
        name='more_vc',
        label='More version control',
        )
    def act_more_vc(self, action, *args):
        pass

class FilesystemContextMixin(object):

    @actions.action(
        name='filemanager',
        stock_id='gtk-filemanager',
        label='Browse'
        )
    def act_filemanager(self, action, filename):
        directory = self.get_directory(filename)
        self.boss.call_command('filemanager',
                               'browse',
                               directory=filename)

    @actions.action(
        name='terminal',
        stock_id='gtk-terminal',
        label='Terminal'
        )
    def act_terminal(self, action, filename):
        directory = self.get_directory(filename)
        self.boss.call_command('terminal',
                               'execute_shell',
                               kwdict={'directory': directory})

    @actions.action(
        name='grepper',
        stock_id='gtk-searchtool',
        label='Search for text',
        )
    def act_search(self, action, filename):
        directory = self.get_directory(filename)
        self.boss.call_command('grepper', 'find_interactive',
                               directories=[directory])


    def get_directory(self, filename):
        if not os.path.isdir(filename):
            filename = os.path.dirname(filename)
        return filename

class DirectoryContext(FilesystemContextMixin,
                  VersionControlContextMixin,
                  ActionContext,
                  ):

    def get_menu_definition(self):
        return """
                <popup>
                    <menuitem action="filemanager" />
                    <menuitem action="terminal" />
                    <menuitem action="grepper" />
                    <separator />
                    <menuitem action="vcs_update" />
                    <menuitem action="vcs_commit" />
                    <menu action="more_vc">
                        <menuitem action="vcs_revert" />
                        <menuitem action="vcs_remove" />
                        <menuitem action="vcs_diff" />
                        <menuitem action="vcs_add" />
                    </menu>
               </popup>
               """



class FileContext(DirectoryContext):

    def create_menu(self):
        menu = ActionContext.create_menu(self)
        ow = self.get_widget('/popup/open_with')
        open_with_menu = self.boss.call_command('openwith',
            'get_openers_menu', filename=self.action_args[0])
        ow.set_submenu(open_with_menu)
        return menu

    @actions.action(
        name='open_with',
        label='Open With',
        )
    def act_open_with(self, action, *args):
        """Base open with menu"""

    def get_menu_definition(self):
        return """
                <popup>
                    <menuitem action="filemanager" />
                    <menuitem action="terminal" />
                    <separator />
                    <menuitem action="vcs_diff" />
                    <menuitem action="vcs_commit" />
                    <menuitem action="vcs_revert" />
                    <menu action="more_vc">
                        <menuitem action="vcs_update" />
                        <menuitem action="vcs_add" />
                        <menuitem action="vcs_remove" />
                    </menu>
                    <separator />
                    <menuitem action="open_with" />
               </popup>
               """

    
if __name__ == '__main__':
    class ms:
        NAME = 'ms'
    w = gtk.Window()
    w.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    ac = FileContext(ms(), 'foo')
    m = ac.create_menu()
    w.show_all()
    def c(win, evt):
        m.popup(None, None, None, evt.button, evt.time)
    w.connect('button-press-event', c) 
    gtk.main()
    

CONTEXTS = [('file_vc', 'When an action is in the context of a single file'),
            ('directory', 'When an action is in the context of a directory'),
            ('project_directory', 'When an action is in the context of a directory'),
            ('project', 'When an action is in the context of a directory'),
            ('file_parent', '')
            ]

Service = Contexts
