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

import base
import pkg_resources
import traceback
from cStringIO import StringIO

SERVICE_GROUPS = ['services', 'editors', 'languages', 'plugins']

class service_manager(base.pidagroup):
    """Top level services component group."""

    def init(self):
        base.pidagroup.init(self, None)
        self.__display_names = {}
        self.__available =  {'services': {},
                             'editors': {},
                             'plugins': {},
                             'languages':{}}

    def load_all(self, groups=SERVICE_GROUPS):
        self.log.debug('finding all services')
        for group in groups:
            self.__load_entrypoints(group)
        # load all the services, they are compulsory
        self.__check_importants_loaded(self.__available['services'])
        self.log.debug('loading core services')
        for svc in self.__available['services']:
            self.__load_service('services', svc)
        self.__check_importants_loaded([i.NAME for i in self])
        # load the required plugins
        self.log.debug('loading required plugins')
        for plugin in self.__available['plugins']:
            self.__load_service('plugins', plugin)

    def load_editor(self):
        # load one editor
        editor_type = self.get('editormanager').get_editor_name()
        self.__load_service('editors', editor_type)

    def __load_entrypoints(self, group):
        self.log.debug('finding services in %s', group)
        for ep in pkg_resources.iter_entry_points('pida.%s' % group):
            self.log.debug('found entry point %s.%s', group, ep.name)
            self.__load_entrypoint(group, ep)

    load_entrypoints = __load_entrypoints

    def __load_entrypoint(self, group, entrypoint):
        try:
            cls = entrypoint.load()
            cls.boss = self.boss
            cls.NAME = entrypoint.name
            if not hasattr(cls, 'display_name'):
                cls.display_name = cls.NAME
                self.log.debug('Services should have a display name %s',
                                cls.NAME)
            self.__display_names[cls.NAME] = cls.display_name
            self.__available[group][cls.NAME] = cls
            
        except:
            buff = StringIO()
            traceback.print_exc(file=buff)
            self.log.warn('failed to import %s.%s \n%s',
                           group, entrypoint, buff.getvalue())
            
    load_entrypoint = __load_entrypoint

    def __load_service(self, group, name):
        self.log.debug('loading service %s.%s', group, name)
        try:
            cls = self.__available[group][name]
        except KeyError:
            cls = None
            self.log.warn('service not found %s %s', group, name)
        if cls is not None:
            try:
                inst = cls()
            except TypeError:
                inst = cls(self.boss)
            if inst is not None:
                self.add(inst.NAME, inst)

    load_service = __load_service
        
    def __check_importants_loaded(self, svclist):
        for name in ['window', 'editormanager', 'buffermanager',
                     'projectmanager']:
            if name not in svclist:
                raise RuntimeError('Important service "%s" not loaded. Fatal' %
                                    name)

    def get_display_name(self, servicename):
        if servicename in self.__display_names:
            return self.__display_names[servicename]

    def bind(self):
        for service in self:
            service.bind_events()
        for service in self:
            service.bind_bases()
        for service in self:
            service.bind()

    def reset(self):
        for service in self:
            service.reset()

    def stop(self):
        for service in self:
            service.stop()
        


