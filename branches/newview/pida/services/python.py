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

# system import(s)
import os

import pida.core.actions as actions

# pida core import(s)
from pida.core import service

defs = service.definitions
types = service.types


class python(service.service):

    class python_execution(defs.optiongroup):
        """Options pertaining to python execution"""
        class python_executable(defs.option):
            """The command to call when executing python scripts."""
            rtype = types.string
            default = 'python'
        class python_shell(defs.option):
            """The command to call when executing a python shell."""
            rtype = types.string
            default = 'python'

    def cmd_execute_shell(self):
        py = self.opt('python_execution', 'python_shell')
        command_args=[py]
        self.boss.call_command('terminal', 'execute',
                               command_args=command_args,
                               icon_name='execute',
                               short_title='Python Shell')

    def cmd_execute_file(self, filename):
        py = self.opt('python_execution', 'python_executable')
        command_args=[py, filename]
        self.boss.call_command('terminal', 'execute',
                               command_args=command_args,
                               icon_name='execute')

    def act_python_shell(self, action):
        """Start an interactive python shell."""
        self.call('execute_shell')

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_python" action="base_python_menu">
                <menuitem name="pyshell" action="python+python_shell" />
                </menu>
                </menubar>
               """

    class python(defs.project_type):
        project_type_name = 'python'

        class general(defs.optiongroup):
            """General options for Python projects"""
            class source_directory(defs.option):
                """The directory containing source code."""
                rtype = types.directory
                default = os.path.expanduser('~')
            class python_binary_location(defs.option):
                """The location of the python binary"""
                rtype = types.file
                default = '/usr/bin/python'

        class execution(defs.optiongroup):
            """Options relating to executing the project"""
            class project_file_to_execute(defs.option):
                """The python file to run for this project"""
                rtype = types.file
                default = ''                
            class use_python_to_execute(defs.option):
                rtype = types.boolean
                default = True

        @actions.action(
            default_accel='<Shift><Control>x'
        )
        def act_project_execute(self, action):
            """Execute the current project."""
            proj = self.boss.call_command('projectmanager',
                                          'get_current_project')
            projfile = proj.get_option('execution',
                        'project_file_to_execute').value
            use_py = proj.get_option('execution',
                        'use_python_to_execute').value
            if use_py:
                shell_cmd = 'python'
            else:
                shell_cmd = 'bash'
            if projfile:
                self.service.boss.call_command('terminal', 'execute',
                    command_args=[shell_cmd, projfile], icon_name='run')
            else:
                self.service.log.info('project has not set an executable')
        
        # XXX: this should be on gazpach service
        @actions.action(
            label="Add UI Form...",
        )
        def act_add_ui_form(self, action):
            """Add a user interface form to the current project."""
            def callback(name):
                if not name.endswith('.glade'):
                    name = '%s.glade' % name
                proj = self.boss.call_command('projectmanager',
                                              'get_current_project')
                filepath = os.path.join(proj.source_directory, name)
                self.service.boss.call_command('gazpach', 'create',
                                               filename=filepath)
            self.service.boss.call_command('window', 'input',
                                            callback_function=callback,
                                            prompt='Form Name')

        def get_menu_definition(self):
            return """
            <menubar>
            <menu name="base_project" action="base_project_menu">
            <separator />
            <menuitem name="addform" action="python+project+add_ui_form" />
            <menuitem name="expyproj" action="python+project+project_execute" />
            <separator />
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
            <separator />
            <toolitem name="runproj" action="python+project+project_execute" />
            </placeholder>
            <placeholder name="VcToolbar">
            </placeholder>
            <placeholder name="ToolsToolbar">
            </placeholder>
            </toolbar>
            """


    class python_executor(defs.language_handler):
        file_name_globs = ['*.py']

        first_line_globs = ['*/bin/python']

        def init(self):
            self.__document = None
            self.__cached = self.cached = {}

        def load_document(self, document):
            self.__document = document

        def act_execute_current_file(self, action):
            """Runs the current python script"""
            self.service.call('execute_file',
                              filename=self.__document.filename)

        def get_menu_definition(self):
            return """
                <menubar>
                <menu name="base_python" action="base_python_menu">
                <menuitem name="expyfile" action="python+language+execute_current_file" />
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
                <separator />
                <toolitem name="runpy" action="python+language+execute_current_file"/>
                <separator />
                </placeholder>
                <placeholder name="VcToolbar">
                </placeholder>
                <placeholder name="ToolsToolbar">
                </placeholder>
                </toolbar>
                """

Service = python
