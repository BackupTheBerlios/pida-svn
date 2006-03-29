# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 The PIDA Project

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

# pIDA imports
import base
import event
import command
import shelve
import registry
import actions
import definitions

types = registry.types


import gtk

# system imports
import os

from actions import split_function_name
from pida.utils.servicetemplates import build_optiongroup_from_class
from errors import CommandNotFoundError

class options_mixin(object):
    """Configuration options support."""
    __options__ = []

    def init(self):
        self.__options = registry.registry()
        self.__init()
        self.__load()

    def __init(self):
        for classobj in self.__class__.__options__:
            group = build_optiongroup_from_class(classobj, self.__options)

    def __load(self):
        path = os.path.join(self.boss.pida_home, 'conf',
                            '%s.conf' % self.NAME)
        self.__options.load(path)

    def get_options(self):
        return self.__options
    options = property(get_options)

    def get_option(self, groupname, optionname):
        group = self.options.get(groupname)
        if group is not None:
            option = group.get(optionname)
            if option is not None:
                return option.value

    def set_option(self, groupname, optionname, value):
        group = self.options.get(groupname)
        if group is not None:
            option = group.get(optionname)
            if option is not None:
                option.value = value
        

    opt = get_option


class commands_mixin(object):
    """Command support."""
    __commands__ = []

    def init(self):
        self.__commands = command.commandgroup(self.NAME)
        self.__init()

    def __init(self):
        for cmdfunc in self.__class__.__commands__:
            name = split_function_name(cmdfunc.func_name)
            selffunc = getattr(self, cmdfunc.func_name)
            self.__commands.new(name, selffunc, [])

    def get_commands(self):
        return self.__commands
    commands = property(get_commands)

    def call(self, commandname, **kw):
        command = self.commands.get(commandname)
        if command is not None:
            self.log.debug('calling "%s" with "%s"', commandname, kw)
            result = self.__call_command(command, **kw)
            self.log.debug('called "%s" with result "%s"',
                           commandname, result)
            return result
        else:
            raise CommandNotFoundError(commandname)

    def __call_command(self, command, **kw):
        return command(**kw)

    def call_external(self, servicename, commandname, **kw):
        svc = self.get_service(servicename)
        return svc.call(commandname, **kw)


class actions_mixin(object):

    __actions__ = []

    def init(self):
        self.__action_group = gtk.ActionGroup(self.NAME)
        self.__init()

    def bind(self):
        menudef = self.get_menu_definition()
        if menudef:
            self.boss.call_command('window', 'register_action_group',
                actiongroup=self.action_group, uidefinition=menudef)

    def __init(self):
        # First we need to get the methods instead of the functions
        # create_actions accepts only methods and not class functions
        get_method = lambda func: getattr(self, func.__name__)
        meths = map(get_method, self.__class__.__actions__)
        # Now we can create the actions
        acts = actions.create_actions(meths, self.NAME)
        # Finally for each action we add it to the group
        add_action = self.__action_group.add_action
        map(add_action, acts)

    def get_action_group(self):
        return self.__action_group
    action_group = property(get_action_group)


class events_mixin(object):

    __events__ = []
    
    def init(self):
        self.__events = event.event()
        for evtclass in self.__events__:
            evtname = evtclass.__name__
            self.__events.create_event(evtname)

    def get_events(self):
        return self.__events
    events = property(get_events)


class bindings_mixin(object):

    __bindings__ = []

    def init(self):
        pass

    def bind(self):
        for bndfunc in self.__bindings__:
            evtstring = split_function_name(bndfunc.func_name)
            servicename, eventname = evtstring.split('_', 1)
            svc = self.get_service(servicename)
            func = getattr(self, bndfunc.func_name)
            if svc.events.has_event(eventname):
                svc.events.register(eventname, func)
            else:
                self.log.error('event "%s" does not exist', eventname)


class document_type_mixin(object):

    __documenttypes__ = []
    
    def init(self):
        pass

    def bind(self):
        for handler in self.__documenttypes__:
            handler.service = self
            svc = self.get_service('documenttypes')
            svc.call('register_file_handler', handler=handler)


class language_type_mixin(object):
    
    __languagetypes__ = []

    def init(self):
        pass

    def bind(self):
        for handler_type in self.__class__.__languagetypes__:
            handler_type.service = self
            self.boss.call_command('languagetypes',
                                   'register_language_handler',
                                   handler_type=handler_type)

    def bnd_buffermanager_document_modified(self, document):
        if hasattr(self, 'uncache'):
            self.uncache(document)

    plugin_view = None


class project_type_mixin(object):

    __projecttypes__ = []

    def init(self):
        pass

    def bind(self):
        for handler_type in self.__class__.__projecttypes__:
            handler_type.service = self
            self.boss.call_command('projecttypes',
                                   'register_project_type',
                                   handler_type=handler_type)


from views import view_mixin

service_base_classes =  [options_mixin,
                         commands_mixin,
                         events_mixin,
                         bindings_mixin,
                         actions_mixin,
                         document_type_mixin,
                         language_type_mixin,
                         project_type_mixin,
                         view_mixin]


binding_base_classes = [document_type_mixin,
                        language_type_mixin,
                        project_type_mixin]


class service_type(type):
    """The service metaclass.

    """

    available_services = {}

    attribute_map = {
        'cmd': '__commands__',
        'bnd': '__bindings__',
        'act': '__actions__',
        'optiongroup': '__options__',
        'action': '__actions__',
        'language_handler': '__languagetypes__',
        'document_handler': '__documenttypes__',
        'project_type': '__projecttypes__',
        'database': '__databases__',
        'event': '__events__',
        'View': '__views__',
    }

    def __new__(cls, name, bases, classdict):
        bases = tuple(list(bases) + service_base_classes)
        new_type = type.__new__(cls, name, bases, classdict)
        cls.register_functions(new_type)
        cls.available_services[new_type.NAME] = new_type
        return new_type
    
    def register_functions(cls, newtype):
        for attrname in cls.attribute_map.values():
            setattr(newtype, attrname, [])
        for attrtype, obj in cls.get_functions(newtype):
            if attrtype in cls.attribute_map:
                getattr(newtype, cls.attribute_map[attrtype]).append(obj)

    register_functions = classmethod(register_functions)

    def get_functions(newtype):
        for attrname in dir(newtype):
            item = getattr(newtype, attrname)
            if callable(item):
                k = attrname
                if getattr(item, '__bases__', []):
                    attrtype = item.__bases__[0].__name__
                elif 'cmd_' in k or 'bnd_' in k or 'act' in k:
                    attrtype = k.split('_', 1)[0]
                else:
                    continue
                yield attrtype, item

    get_functions = staticmethod(get_functions)


class service_base(base.pidacomponent):
    """The service base class.

    Brings together the mixins, and the metaclass. Automatically registers
    definitions as the correct type of attribute for registry on instantiation
    and also bindings to be executed after all services are loaded. General
    utility methods not included in any mixin are also icluded here.
    """
    __metaclass__ = service_type

    NAME = ''

    def __init__(self, boss):
        """Constructor
        
        @var boss the pida boss object
        """
        self.boss = boss
        for baseclass in service_base_classes:
            baseclass.init(self)
        base.pidacomponent.__init__(self)

    def init(self):
        pass
    
    def start(self):
        pass

    def bind_events(self):
        bindings_mixin.bind(self)
        actions_mixin.bind(self)

    def bind_bases(self):
        for baseclass in binding_base_classes:
            baseclass.bind(self)

    def bind(self):
        pass

    def reset(self):
        pass

    def get_service(self, servicename):
        return self.boss.get_service(servicename)

    def get_menu_definition(self):
        return '<menubar /><toolbar />'

    def stop(self):
        pass


class service(service_base):
    """A pIDA Service.
        
    The methods defined in this class itself are events in the lifetime of a
    service. They are all to be overriden by subclasses.
    """

    def start(self):
        """Called immediately after instantiation of the service.
            
        The service can gurantee that its configuration options have been
        loaded from disk, but must not attempt to rely on the existence of
        any other service.
        """

    def reset(self):
        pass

    def stop(self):
        pass
