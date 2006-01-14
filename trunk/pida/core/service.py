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

# pIDA imports
import base
import event
import command
import shelve
import registry
import databases

import definitions

types = registry.types


import gtk

# system imports
import os


import pida.utils.servicetemplates as servicetemplates


split_function_name = servicetemplates.split_function_name
get_actions_for_funcs = servicetemplates.get_actions_for_funcs
build_optiongroup_from_class = servicetemplates.build_optiongroup_from_class


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
            self.log.warn('command not found %s', commandname)

    def __call_command(self, command, **kw):
        return command(**kw)

    def call_external(self, servicename, commandname, **kw):
        svc = self.get_service(servicename)
        if svc is not None:
            return svc.call(commandname, **kw)


class data_mixin(object):
    """Data support."""
    __databases__ = []

    def init(self):
        self.__databases = {}
        self.__schemas = {}
        self.__views = {}
        self.__datanames = {}
        self.__dataview_types = {}
        self.__init()

    def __init(self):
        dirpath = os.path.join(self.boss.pida_home, 'data', self.NAME)
        if len(self.__databases__):
            if not os.path.exists(dirpath):
                os.mkdir(dirpath)
            for dbclass in self.__class__.__databases__:
                filepath = os.path.join(dirpath, '%s.dat' %
                                        dbclass.__name__)
                name = dbclass.__name__
                self.__databases[name] = databases.data_base(filepath)
                data_view = getattr(dbclass, 'DATA_VIEW', None)
                self.__dataview_types[name] = data_view
                fields = []
                for fieldname in dir(dbclass):
                    field = getattr(dbclass, fieldname)
                    if len(getattr(field, '__bases__', [])):
                        if field.__bases__[0].__name__ == 'field':
                            fields.append((fieldname, field.rtype,
                                           field.default, field.__doc__))
                self.__schemas[name] = fields

    def get_databases(self):
        return self.__databases
    databases = property(get_databases)

    def get_schema(self, name):
        return self.__schemas[name]
    schema = property(get_schema)

    def close_databases(self):
        for name, db in self.databases.iteritems():
            db.close()

    def add_data_item(self, dataname, key, item=None):
        if self.has_database(dataname):
            db = self.databases[dataname]
            db[key] = item
            db.sync()
            self.cb_data_changed(dataname)

    def create_data_item(self, dataname, itemname, **kw):
        if self.has_database(dataname):
            schema = self.__schemas[dataname]
            record = databases.data_record()
            for fieldname, rtype, default, doc in schema:
                if fieldname in kw:
                    value = kw[fieldname]
                else:
                    value = default
                setattr(record, fieldname, value)
            self.add_data_item(dataname, itemname, record)
            return record

    def iter_database(self, dataname):
        if self.has_database(dataname):
            db = self.databases[dataname]
            for k in db:
                yield k, db[k]

    def create_data_view(self, dataname):
        if self.has_database(dataname):
            if dataname not in self.__views:
                schema = self.__schemas[dataname]
                view_type = self.__dataview_types[dataname]
                if view_type is not None:
                    view = view_type(self, prefix='data_view')
                    view.set_database(dataname, self.databases[dataname], schema)
                    self.boss.call_command('window', 'append_page',
                                           bookname='view', view=view)
                    self.__views[dataname] = view
                    self.__datanames[view.unique_id] = dataname
                else:
                    raise NotImplementedError(
                        '%s Has not specified a DATA_VIEW' % self.NAME)

    def cb_data_view_controlbar_clicked_close(self, view, toolbar, name):
        assert view in self.__views.values()
        if self.confirm_data_view_controlbar_clicked_close(view):
            view.remove()
            dataname = self.__datanames[view.unique_id]
            del self.__views[dataname]
            del self.__datanames[view.unique_id]
            view.destroy()

    def cb_data_view_newitem(self, dataname, itemname):
        self.create_data_item(dataname, itemname)

    def cb_data_view_applied(self, dataname):
        pass

    def cb_data_changed(self, dataname):
        pass

    def confirm_data_view_controlbar_clicked_close(self, view):
        return True

    def has_database(self, dataname):
        has = dataname in self.__schemas
        if not has:
            self.log.info('attempt to access non-existing database %s',
                          dataname)
        return has

    def raise_data_view(self, dataname=None):
        if dataname is None:
            if len(self.__views) == 1:
                for k in self.__views:
                    self.__views[k].raise_page()
            else:
                raise TypeError('Must specify dataname when there is '
                                'more than one data view')
        else:
            if dataname in self.__views:
                self.__views[dataname].raise_page()
            else:
                self.log.warn('data view %s is unavailable', dataname)


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
        for action in get_actions_for_funcs(self.__class__.__actions__,
                                                self):
            self.__action_group.add_action(action)

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
            if svc is not None:
                func = getattr(self, bndfunc.func_name)
                try:
                    svc.events.register(eventname, func)
                except AssertionError:
                    self.log.info('event "%s" does not exist', eventname)


class document_type_mixin(object):

    __documenttypes__ = []
    
    def init(self):
        pass

    def bind(self):
        for handler in self.__documenttypes__:
            handler.service = self
            svc = self.get_service('documenttypes')
            if svc:
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


class plugin_view_mixin(object):

    plugin_view_type = None

    def init(self):
        self.__view = None

    def create_plugin_view(self, **kw):
        if self.plugin_view_type is not None:
            self.__view = self.plugin_view_type(self, 'plugin_view', **kw)

    def get_plugin_view(self):
        if self.__view is None:
            self.create_plugin_view()
        return self.__view

    plugin_view = property(get_plugin_view)


class lang_view_mixin(object):
    """Create a language view mixin based on view type."""

    lang_view_type = None

    def init(self):
        self.__view = None

    def create_lang_view(self, *args, **kwargs):
        if self.lang_view_type:
            self.__view = self.lang_view_type(self,
                                              prefix='lang_view')

    def get_lang_view(self):
        if self.__view is None:
            self.create_lang_view()
        return self.__view

    lang_view = property(get_lang_view)


class single_view_mixin(object):

    single_view_type = None
    single_view_book = 'content'

    def init(self):
        self.__view = None



    def create_single_view(self, *args, **kwargs):
        if self.single_view_type is not None:
            if self.__view is None:
                self.__view = self.single_view_type(self,
                    prefix='single_view', *args, **kwargs)
                self.__view.connect('removed', self.cb_single_view_removed)
                self.boss.call_command('window', 'append_page',
                                       bookname=self.single_view_book,
                                       view=self.__view)
            self.__view.raise_page()
            return self.__view

    def raise_single_view(self, name):
        if self.__view is not None:
            self.__view.raise_page(name)
        else:
            self.create_single_view()

    def cb_single_view_controlbar_clicked_close(self, view, toolbar, name):
        assert(view is self.__view)
        if self.confirm_single_view_controlbar_clicked_close(view):
            self.__view.remove()

    def cb_single_view_controlbar_clicked_detach(self, view, toolbar, name):
        assert(view is self.__view)
        try:
            ggp = view.get_parent().get_parent().get_parent()
        except:
            ggp = None
        if ggp.__class__.__name__ == 'external_window':
            bookname = self.single_view_book
        else:
            bookname = 'ext'
        self.__view.detach()
        self.boss.call_command('window', 'append_page',
                                bookname=bookname,
                                view=self.__view)
        self.__view.raise_page()
            

    def cb_single_view_removed(self, view):
        self.__view.destroy()
        self.__view = None
        self.cb_single_view_closed(view)

    def cb_single_view_closed(self, view):
        pass

    def confirm_single_view_controlbar_clicked_close(self, view):
        return True

    def get_single_view(self):
        return self.__view

    single_view = property(get_single_view)


class multi_view_mixin(object):

    def init(self):
        self.__views = {}

    def create_multi_view(self, *args, **kw):
        if self.multi_view_type is None:
            return
        view = self.multi_view_type(self, prefix='multi_view', *args, **kw)
        self.__views[view.unique_id] = view
        self.boss.call_command('window', 'append_page',
                                bookname=self.multi_view_book,
                                view=view)
        return view

    def raise_multi_view(self, unique_id):
        if unique_id in self.__views:
            self.__views[unique_id].raise_page()
            return self.__views[unique_id]
        else:
            self.log.info('attempt to raise a non-existing multiview')

    def cb_multi_view_controlbar_clicked_close(self, view, toolbar, name):
        if self.confirm_multi_view_controlbar_clicked_close(view):
            def closed():
                view.remove()
                self.cb_multi_view_closed(view)
                del self.__views[view.unique_id]
                #view.destroy()
            gtk.idle_add(closed)

    def cb_multi_view_controlbar_clicked_detach(self, view, toolbar, name):
        try:
            ggp = view.get_parent().get_parent().get_parent()
        except:
            ggp = None
        if ggp.__class__.__name__ == 'external_window':
            bookname = self.multi_view_book
        else:
            bookname = 'ext'
        view.detach()
        self.boss.call_command('window', 'append_page',
                                bookname=bookname,
                                view=view)
        view.raise_page()

    def confirm_multi_view_controlbar_clicked_close(self, view):
        return True

    def cb_multi_view_closed(self, view):
        pass

    def get_multi_view(self, unique_id):
        return self.__views.get(unique_id, None)

    def get_multi_views(self):
        for view in self.__views.values():
            yield view
    multi_views = property(get_multi_views)


service_base_classes =  [options_mixin,
                         commands_mixin,
                         events_mixin,
                         bindings_mixin,
                         data_mixin,
                         document_type_mixin,
                         language_type_mixin,
                         actions_mixin,
                         plugin_view_mixin,
                         single_view_mixin,
                         lang_view_mixin,
                         multi_view_mixin,
                         project_type_mixin]


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
        'event': '__events__'
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
        self.start()
    
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
        return ''

    def stop(self):
        pass


class service(service_base):
    """A pIDA Service.
        
    The methods defined in this class itself are efvents in the lifetime of a
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
