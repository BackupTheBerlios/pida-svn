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

import actions
import registry
import base
import os
from pida.utils.vc import Vc

import pida.utils.servicetemplates as servicetemplates

def get_first_base(classobj):
    if getattr(classobj, '__bases__', []):
        return classobj.__bases__[0].__name__

def is_first_base_option(classobj):
    firstbase = get_first_base(classobj)
    if firstbase is not None:
        return firstbase == 'optiongroup'
    else:
        return False

class project(base.pidacomponent):

    def init(self, project_type, file_name):
        self.__project_type = project_type
        self.__options_file = file_name
        self.__vcs = None
        self.__registry = project_type.build_raw_registry()
        self.__registry.load(file_name)
        self.__registry.file_intro = '#%s' % project_type.name
        self.__browse_directory = None

    def get_project_type(self):
        return self.__project_type
    project_type = property(get_project_type)
    
    def get_name(self):
        filename =  os.path.basename(self.__options_file)
        name = filename.rsplit('.', 1)[0]
        return name
    name = property(get_name)

    def get_options(self):
        return self.__registry
    options = property(get_options)

    def get_option(self, group, name):
        group = self.options.get(group)
        if group is not None:
            option = group.get(name)
            return option

    def get_option_value(self, group, name):
        option = self.get_option(group, name)
        if option is not None:
            return option.value

    def get_source_directory(self):
        return self.get_option_value('general', 'source_directory')
    source_directory = property(get_source_directory)

    def get_browse_directory(self):
        if self.__browse_directory is None:
            self.__browse_directory = self.source_directory
        return self.__browse_directory

    def set_browse_directory(self, directory):
        self.__browse_directory = directory

    browse_directory = property(get_browse_directory, set_browse_directory)

    def get_vcs_name(self):
        if self.vcs is None or self.vcs.NAME == 'Null':
            return 'no version control'
        else:
            return self.vcs.NAME
    vcs_name= property(get_vcs_name)

    def get_vcs(self):
        source_dir = self.source_directory
        if source_dir is not None:
            if self.__vcs is None:
                self.__vcs = self.boss.call_command('versioncontrol',
                                                    'get_vcs_for_directory',
                                                    directory=source_dir)
            return self.__vcs
    vcs = property(get_vcs)

    def get_project_filename(self):
        return self.__options_file
    project_filename = property(get_project_filename)


class project_type(actions.action_handler):

    type_name = 'project'
    project_type_name = 'project'

    def create_project(self, file_name):
        pass

    def build_raw_registry(self):
        reg = registry.registry()
        for attr in dir(self):
            classobj = getattr(self, attr)
            if is_first_base_option(classobj):
                servicetemplates.build_optiongroup_from_class(classobj, reg)
        return reg

    def get_name(self):
        return self.project_type_name
    name = property(get_name)


from model import Model, ModelGroup
from views import ProjectPropertyPage, ProjectTree


PROJECT_DATA_ATTRS = [
    'name',
    'uses_source',
    'source_directory',
    'uses_vc',
]

class Project(Model):

    def __init__(self):
        self.name = ''
        self.uses_source = True
        self.source_directory = ''
        self.uses_vc = True
        self.uses_build = False
        self.uses_execution = False
        self.execution_command_base = ''
        self.execution_chdir = True
        self.uses_unittests = False
        self.unittest_command_base = ''
        self.build_command = None
        self.build_directory = None

    def delayed_notify(self, attr):
        def _s():
                self.notify_proxies('execution_command')
        gobject.idle_add(_s)

    def notify_proxies(self, attr):
        """Notify proxies that an attribute value has changed."""
        if attr == 'execution_command_base':
            self.delayed_notify('execution_command')
        super(Project, self).notify_proxies(attr)

    def get_execution_command(self):
        try:
            ex = self.execution_command_base % self.__dict__
        except:
            ex = self.execution_command_base
        return ex

    execution_command = property(get_execution_command)

    def get_unittest_command(self):
        try:
            ex = self.unittest_command_base % self.__dict__
        except:
            ex = self.unittest_command_base
        return ex

    unittest_command = property(get_unittest_command)


    def get_vcname(self):
        if self.uses_source and self.uses_vc:
            if self.source_directory:
                vc = Vc(self.source_directory)
                if vc.NAME != 'Null':
                    return vc.NAME
        return None

    vc_name = property(get_vcname)


class ProjectGroup(ModelGroup):

    page_type = ProjectPropertyPage
    tree_type = ProjectTree

    def register_dependents(self):
        o = self._observer
        o.register_dependent('execution_command', 'execution_command_base')
        o.register_dependent('vc_name', 'source_directory')
        o.register_dependent('unittest_command', 'unittest_command_base')

