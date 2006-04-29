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

from pida.model import model, attrtypes as types

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

class ProjectDefinition(object):
    __order__ = ['general', 'source', 'build', 'execution',
                 'testing', 'gui']

    class general:
        """General options relating to the project"""
        __order__ = ['name', 'filename',  'browse_directory']
        label = 'General'
        stock_id = 'gtk-preferences'

        class name:
            """The name you would like to refer to the project as"""
            label = 'Project Name'
            rtype = types.string
            default = 'unnamed'

        class filename:
            """The project file location."""
            label = 'Saved as'
            rtype = types.readonly

            def fget(self):
                return self.__model_ini_filename__

        class browse_directory:
            """Select a source directory for the project"""
            rtype = types.readonly
            label = 'Last Browsed'
            default = '/'
            hidden = True

    class source:
        """Options relating to source code for the project"""
        label = 'Source'
        stock_id = 'gtk-new'
        __order__ = ['uses', 'directory',
                     'uses_vc', 'vc_name']
        class uses:
            """Whether the project has source code"""
            rtype = types.boolean
            label = 'Has Source Code'
            default = True

        class directory:
            """Select a source directory for the project"""
            rtype = types.directory
            label = 'Source Directory'
            default = '/'
            sensitive_attr = 'source__uses'

        class uses_vc:
            """Whether the project uses version control"""
            rtype = types.boolean
            label = 'Uses Version Control'
            default = True
            sensitive_attr = 'source__uses'

        class vc_name:
            """The version control system"""
            rtype = types.readonly
            label = 'System'
            sensitive_attr = 'source__uses_vc'
            dependents = ['source__directory']

            def fget(self):
                from pida.utils.vc import Vc
                if self.source__uses and self.source__uses_vc:
                    vc = Vc(self.source__directory)
                    if vc.NAME != 'Null':
                        return vc.NAME
                return 'None'

    class build:
        """Options relating to the building of this project"""
        label = 'Build'
        stock_id = 'gtk-convert'
        __order__ = ['uses', 'command_base', 'command']

        class uses:
            """Whether this project uses building"""
            rtype = types.boolean
            label = 'Uses build'
            default = True

        class command_base:
            """The build command"""
            rtype = types.string
            label = 'Build command'
            default = ''
            sensitive_attr = 'build__uses'

        class command:
            """The build command as it will be executed"""
            rtype = types.readonly
            label = 'Actual build command'
            sensitive_attr = 'build__uses'
            dependents = ['build__command_base']

            def fget(self):
                return self.__model_interpolate__(self.build__command_base)

    class execution:
        """Options relating to executing this project"""
        label = 'Execution'
        stock_id = 'gtk-execute'
        __order__ = ['uses', 'command_base', 'command']

        class uses:
            """Whether this project uses execution"""
            rtype = types.boolean
            label = 'Uses execution'
            default = True

        class command_base:
            """The execution command"""
            rtype = types.string
            label = 'Execution command'
            default = ''
            sensitive_attr = 'execution__uses'

        class command:
            """The execution command as it will be executed"""
            rtype = types.readonly
            label = 'Actual build command'
            sensitive_attr = 'execution__uses'
            dependents = ['execution__command_base']

            def fget(self):
                return self.__model_interpolate__(
                    self.execution__command_base)

    class testing:
        """Options relating to unit testing this project"""
        label = 'Testing'
        stock_id = 'gtk-dialog-warning'
        __order__ = ['uses', 'command_base', 'command']

        class uses:
            """Whether this project uses unit testing"""
            rtype = types.boolean
            label = 'Uses testing'
            default = True

        class command_base:
            """The testing command"""
            rtype = types.string
            label = 'Testing command'
            default = ''
            sensitive_attr = 'testing__uses'

        class command:
            """The execution command as it will be executed"""
            rtype = types.readonly
            label = 'Actual unit testing command'
            sensitive_attr = 'testing__uses'
            dependents = ['testing__command_base']

            def fget(self):
                return self.__model_interpolate__(self.testing__command_base)

    class gui:
        """Options relating to graphical user interfaces"""
        label = 'Gui'
        stock_id = 'gtk-terminal'
        __order__ = ['uses', 'location']

        class uses:
            """Whether this project has graphical user interface files"""
            rtype = types.boolean
            label = 'Uses Gui'
            default = True

        class location:
            """Gui file location"""
            label = 'File location'
            rtype = types.directory
            sensitive_attr = 'gui__uses'
            default = '/'

    def __markup__(self):
        from cgi import escape
        mu = '<b>%s</b>' % escape(self.general__name)
        if self.source__uses:
            mu = ('%s (<span color="#0000c0">%s</span>)\n%s'
                    % (mu, escape(self.source__vc_name),
                           escape(self.source__directory)))
        return mu

Project = model.Model.__model_from_definition__(ProjectDefinition)

