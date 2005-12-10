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
        self.__registry = project_type.build_raw_registry()
        self.__registry.load(file_name)
    
    def get_name(self):
        return os.path.basename(self.__options_file)
    name = property(get_name)

    def get_options(self):
        return self.__registry
    options = property(get_options)
    

class project_type(actions.action_handler):

    type_name = 'project'

    def create_project(self, file_name):
        pass

    def build_raw_registry(self):
        reg = registry.registry()
        for attr in dir(self):
            classobj = getattr(self, attr)
            if is_first_base_option(classobj):
                servicetemplates.build_optiongroup_from_class(classobj, reg)
        return reg
                


