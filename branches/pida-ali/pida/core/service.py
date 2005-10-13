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

class Service(base.pidaobject):
    NAME = None
    
    COMMANDS = []
    EVENTS = []
    OPTIONS = []
    OPTIONS_DOC = "Options for service %s" % NAME
    BINDINGS = []

    def __init__(self, *args, **kw):
        if self.NAME is None:
            raise Exception, 'Must have NAME %s' % self.__class__
        base.pidaobject.__init__(self, *args, **kw)
        self.__register_options()
        self.__register_commands()
        self.__register_events()
    
    def register_command(self, name, argumentlist):
        """Register a single command."""
        funcname = "cmd_%s" % name.replace("-", "_")
        if hasattr(self, funcname):
            callback = getattr(self, funcname)
            self.__commands.new(name, callback, argumentlist)
            self.log_debug("new cmd - %s" % funcname)
        else:
            self.log_debug("No callback - %s" % funcname)

    def __register_options(self):
        if self.OPTIONS != []:
            self.__options = self.boss.register_option_group(self.NAME,
                                                             self.OPTIONS_DOC)
            for name, doc, default, typ in self.OPTIONS:
                print typ, 'ss'
                opt = self.__options.add(name, doc, default, typ)
                self.log_debug('new opt - %s' % name)

    def __register_commands(self):
        if self.COMMANDS != []:
            self.__commands = self.boss.register_command_group(self.NAME)
            for name, arglist in self.COMMANDS:
                self.register_command(name, arglist)

    def __register_events(self):
        """Register the events that the service will fire."""
        if self.EVENTS != []:
            self.__events = self.boss.register_event_group(self.NAME)
            events = self.__events.create_events(self.EVENTS)
            for k in events:
                self.log_debug('new evt - %s' % k)

    def __register_bindings(self):
        for group, event in self.BINDINGS:
            funcname = "evt_%s_%s" % (group, event.replace('-', '_'))
            if hasattr(self, funcname):
                callback = getattr(self, funcname)
                self.boss.bind_event(group, event, callback)
                self.log_debug("new bind - %s" % funcname)
            else:
                self.log_debug("No bind - %s" % funcname)

    bind = __register_bindings

    def emit_event(self, event_name, **kw):
        if self.EVENTS != []:
            if self.__events.event_exists(event_name):
                self.log_debug('Emitting: %s' % event_name)
                self.__events.emit(event_name, **kw)
            else:
                self.log_debug('Event Not Found: %s' % event_name)

    def bind_events(self):
        """Bind events that the service will use."""

    def populate(self):
        """Populate any UI elements."""

    def populate_base(self):
        pass

class GuiService(Service):

    VIEW = None

    def populate_base(self):
        if self.VIEW is not None:
            self.__view = self.VIEW()
            self.__view.connect('action', self.cb_toolbar_action)

    def cb_toolbar_action(self, view, name):
        cbname = 'toolbar_action_%s' % name
        if hasattr(self, cbname):
            getattr(self, cbname)()

    def __get_view(self):
        return self.__view
    view = property(__get_view)

