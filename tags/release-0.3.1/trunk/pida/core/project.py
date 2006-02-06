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
                


