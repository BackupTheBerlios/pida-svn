# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

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

"""Pida unit testing framework."""

import gtk
import sys
import os

os.environ['PIDA_HOME'] = '/tmp/pida-tests/'

sys.argv = []
import pida.core.base as base

# Core components
import pida.core.services as services
from pida.core.errors import ServiceNotFoundError

class MockBoss(base.pidacomponent):
    """ The object in charge of everything """
    
    load_services = []

    def __init__(self, application, env):
        self.__application = application
        self.__env = env
        # Set the pidaobject base
        base.set_boss(self)
        self.commands = {}
        base.pidacomponent.__init__(self)

    def start(self):
        """Start Pida."""
        self.__services = services.service_manager()
        self.__services.load_all()
        self.test()
        self.report()

    def test(self):
        pass

    def report(self):
        for com in self.commands:
            print com, len(self.commands[com])
        gtk.idle_add(self.stop)

    def load_service(self, group, name):
        self.__services.load_service(group, name)
        self.__services.bind()
        self.__services.reset()

    def reset(self):
        """Reset live configuration options."""
        self.__services.reset()

    def stop(self):
        self.__services.stop()
        self.__application.stop()

    def call_command(self, servicename, commandname, **kw):
        """Call the named command with the keyword arguments."""
        self.commands.setdefault((servicename, commandname), []).append(kw)
        return None
    
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
        return iter(self.__services)
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
import pida.core.application as application

class FailedTest(Exception):
    pass

class ErrorTest(Exception):
    pass

import nose

class ServiceTest(nose.TestCase):
    
    tested_service = 'terminal'

    def setUp(self):
        mainloop = mainstop = lambda *a: None
        self.app = application.main(MockBoss, mainloop, mainstop)
        self.boss = self.app.boss

    def tearDown(self):
        pass

    def get_test_service(self):
        return self.boss.get_service(self.tested_service)
    _ts = property(get_test_service)
    
    def assert_called(self, sname, name, times=1):
        self.assert_((sname, name) in self.boss.commands)
        self.assert_(len(self.boss.commands[(sname, name)]) == times)

    #def test_execute(self):
    #    ts = self.get_test_service()
    #    ts.call('execute_shell')
    #    self.assert_called('window', 'append_page')

        

        
    
