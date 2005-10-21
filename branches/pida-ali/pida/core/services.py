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

import components

class IService(object):
    """The service interface."""

SERVICES = ['buffermanager', 'contentbook', 'commandline', 'manhole',
'terminal', 'versioncontrol', 'filemanager', 'viewbook', 'topbar']

def import_service(self, name):
    """ Find a named plugin and instantiate it. """
    # import the module
    # The last arg [True] just needs to be non-empty
    try:
        mod = __import__('pida.services.%s' % name, {}, {}, [True])
        cls = mod.Service
    except ImportError, e:
        print ('Plugin "%s" failed to import with: %s' % (name, e))
        cls = None
    return cls

class ServiceManager(components.ComponentGroup):
    """Top level services component group."""
    IMPORT_FUNC = import_service
    def load(self, name):
        """Initialise the named service."""
        self.log_debug('Loading: %s.' % name)
        svc = self.IMPORT_FUNC(name)
        if svc:
            svc.boss = self.boss
            inst = svc()
            if inst:
                self.register(name, inst)
                self.log_debug('Loaded: %s.' % name)
                return inst
        self.log_warn('Not Loaded: %s' % name)

    def load_all(self):
        """Initialise all the services."""
        for name in SERVICES:
            self.load(name)
        self.log_debug('Loaded all services.')

    def register_events(self, name):
        """Register the events for the named service."""

    def register_events_all(self):
        """Register the events for all services."""

    def register_commands(self, name):
        """Register the commands for the named service."""

    def register_commands_all(self):
        """Register the commands for all services."""

    def bind(self):
        for service in self:
            service.bind()

    def populate(self):
        self.log_debug('Populating')
        for service in self:
            self.log_debug('Populating %s' % service)
            service.populate_base()
            service.populate()

    def reset(self):
        for service in self:
            service.reset()


