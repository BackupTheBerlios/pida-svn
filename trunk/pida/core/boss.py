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


import base
import pida.utils.pidalog.log as log

# Core components
import services
from errors import ServiceNotFoundError

class boss(base.pidacomponent):
    """ The object in charge of everything """
    
    def __init__(self, application, env):
        # Set the pidaobject base
        base.pidaobject.boss = self
        base.pidacomponent.__init__(self)
        self.__application = application
        self.__env = env

    def start(self):
        """Start Pida."""
        self.__services = services.service_manager()
        self.__services.load_all()
        self.__editor = self.get_service('editormanager')
        self.__window = self.get_service('window')
        self.__services.bind()
        self.__services.reset()
        try:
            self.call_command('editormanager', 'start')
        except:
            self.log.warn('editor failed to start')
            raise
        try:
            self.call_command('terminal', 'execute_shell')
        except:
            self.log.warn('terminal emulator not configured correctly')

    def reset(self):
        """Reset live configuration options."""
        self.__services.reset()

    def stop(self):
        self.__services.stop()
        self.__application.stop()

    def call_command(self, servicename, commandname, **kw):
        """Call the named command with the keyword arguments."""
        group = self.get_service(servicename)
        return group.call(commandname=commandname, **kw)
    
    def option_value(self, groupname, name):
        """Get the option value for the grouped named option."""
        return self.__config.get_value(groupname, name)

    def get_service(self, name):
        """Get the named service."""
        service = self.__services.get(name)
        if service is None:
            raise ServiceNotFoundError(name)
        return service

    def get_editor(self):
        return self.__editor

    def get_services(self):
        return self.__services.__iter__()
    services = property(get_services)

    def get_service_displayname(self, servicename):
        return self.__services.get_display_name(servicename)

    def get_main_window(self):
        return self.__window.view

    def get_pida_home(self):
        return self.__env.home_dir
    pida_home = property(get_pida_home)

    def get_version(self):
        return self.__env.version
    version = property(get_version)

    def get_positional_args(self):
        return self.__env.positional_args
    positional_args = property(get_positional_args)

    ServiceNotFoundError = ServiceNotFoundError

