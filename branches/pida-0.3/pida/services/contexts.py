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
import os.path

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
        self.__defaults['file'] = file_context()
        self.__defaults['directory'] = directory_context()
        for contextname in ['file', 'directory']:
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
            

class file_context(default_context):

    COMMANDS = [('filemanager', 'filemanager', 'File Manager',
                'Open a file manager in the parent directory of this file'),
                ('terminal', 'terminal', 'Terminal',
                'Open a terminal in the parent directory of this file'),
                ('diff', 'vcs_diff', 'Version Control Diff',
                 'Get the diff on this file')]

    def globals_modifier(self, globaldict):
        return globaldict['filename']

    def command_filemanager(self, filename):
        self.boss.command('filemanager', 'browse',
            directory=self.get_parent_directory(filename))

    def command_terminal(self, filename):
        self.boss.command('terminal', 'execute-vt-shell',
        kwargs={'directory': self.get_parent_directory(filename)})

    def command_diff(self, filename):
        self.boss.command('versioncontrol', 'diff-file',
                          filename=filename)

    def get_parent_directory(self, filename):
        directory = os.path.split(filename)[0]
        return directory


class directory_context(default_context):
    
    COMMANDS = [('filemanager', 'filemanager', 'File Manager',
                 'Browse this directory'),
                ('up', 'up', 'Up',
                 'Browse the parent directoy'),
                ('find', 'find', 'Find',
                 'Find files in this directory'),
                ('new', 'new', 'New',
                 'Create a new file in this directory'),
                ('terminal', 'terminal', 'Terminal',
                'Open a terminal in this directory'),
                ('vcs_diff', 'vcs_diff', 'VCS Statuses',
                 'Get the version statuses of this directory'),
                ('vcs_update', 'vcs_update', 'VCS Update',
                 'update this directory from version control.'),
                ('vcs_commit', 'vcs_commit', 'VCS Commit',
                 'commit this directory to version control.')]

    def globals_modifier(self, globaldict):
        return globaldict['directory']

    def command_filemanager(self, directory):
        self.boss.call_command('filemanager', 'browse', directory=directory)

    def command_find(self, directory):
        self.boss.call_command('grepper', 'find-interactive',
                           directories=[directory])

    def command_new(self, directory):
        self.boss.call_command('newfile', 'create-interactive',
                          directory=directory)

    def command_terminal(self, directory):
        self.boss.call_command('terminal', 'execute_shell',
                          kwdict={'directory': directory})

    def command_up(self, directory):
        if directory != '/':
            parent = os.path.split(directory)[0]
            self.boss.call_command('filemanager', 'browse', directory=parent)

    def command_vcs_diff(self, directory):
        self.boss.call_command('versioncontrol', 'statuses',
                               directory=directory)

    def command_vcs_commit(self, directory):
        self.boss.call_command('versioncontrol', 'commit',
                                directory=directory)

    def command_vcs_update(self, directory):
        self.boss.call_command('versioncontrol', 'update',
                                directory=directory)


CONTEXTS = [('file', 'When an action is in the context of a single file'),
            ('directory', 'When an action is in the context of a directory')]

Service = Contexts
