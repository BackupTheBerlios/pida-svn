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

import pida.core.service as service
import pida.core.project as project

defs = service.definitions
types = service.types

class project_types(service.service):

    def init(self):
        self.__types = {}
        self.__action_groups = {}
        self.__projectsdir = os.path.join(self.boss.pida_home, 'projects')

    class project_type_registered(defs.event):
        pass

    def cmd_register_project_type(self, handler_type):
        handler = handler_type(handler_type.service)
        project_name = handler_type.__name__
        self.__types[project_name] = handler
        type_dir = os.path.join(self.__projectsdir, project_name)
        if not os.path.exists(type_dir):
            os.mkdir(type_dir)
        self.boss.call_command('window', 'register_action_group',
                               actiongroup=handler.action_group,
                               uidefinition=handler.get_menu_definition())
        handler.action_group.set_visible(False)
        self.events.emit('project_type_registered')

    def cmd_get_project_type_names(self):
        for project_name in self.__types:
            yield project_name

    def cmd_load_project(self, project_file_name):
        try:
            f = open(project_file_name, 'r')
            project_type_name = 'project'
            for line in f:
                project_type_name = line.strip().strip('#')
                break
            f.close()
        except OSError, IOError:
            self.log.info('unable to read "%s"', project_file_name)
            return
        if project_type_name not in self.__types:
            project_type_name = 'default'
        if project_type_name in self.__types:
            project_type = self.__types[project_type_name]
            proj = project.project(project_type, project_file_name)
            return proj
    

Service = project_types
