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

class Contexts(service.service):

    class contexts(defs.database):
        #DATA_VIEW = dataview.data_view
        class scripts(defs.field):
            rtype = types.string
            default = ''

    def init(self):
        self.__defaults = {}
        self.__defaults['file_vc'] = file_versioncontrol_context()
        self.__defaults['directory'] = directory_context()
        self.__defaults['project_directory'] = project_directory_context()
        self.__defaults['project'] = project_context()
        self.__defaults['file_parent'] = file_parent_context()
        for contextname in self.__defaults:
            if contextname not in self.databases['contexts']:
                self.add_data_item('contexts', contextname, [])

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
                 'Diff file'),
                 ('vcs_add', 'vcs_add', 'VCS Add',
                 'Add file'),
                 ('vcs_remove', 'vcs_remove', 'VCS Remove',
                 'Remove file'),
                 ('vcs_revert', 'undo', 'VCS revert',
                 'Revert file')]

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

        

CONTEXTS = [('file_vc', 'When an action is in the context of a single file'),
            ('directory', 'When an action is in the context of a directory'),
            ('project_directory', 'When an action is in the context of a directory'),
            ('project', 'When an action is in the context of a directory'),
            ('file_parent', '')
            ]

Service = Contexts
