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

    def __get_options(self):
        return self.__options
    options = property(__get_options)

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

    def reset(self):
        pass

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

    def stop(self):
        pass

class GuiService(Service):

    VIEW = None
    BUTTONS = []
    ICON = None

    def populate_base(self):
        if self.VIEW is not None:
            self.__view = self.VIEW(self.ICON)
            self.__view.connect('action', self.cb_toolbar_action)
            if self.BUTTONS != []:
                for name, icon, doc in self.BUTTONS:
                    self.__view.add_button(name, icon, doc)

    def cb_toolbar_action(self, view, name):
        cbname = 'toolbar_action_%s' % name
        if hasattr(self, cbname):
            getattr(self, cbname)()

    def __get_view(self):
        return self.__view
    view = property(__get_view)

class ServiceWithEditorMixin(object):

    EDITOR_VIEW = None
    PARENT_VIEW = 'viewbook'

    def populate_base(self):
        self.__editorview = None

    def create_editorview(self, *args, **kwargs):
        if self.__editorview is None:
            if self.EDITOR_VIEW is None:
                raise NotImplementedError, "Must specify a EDITORVIEW."
            self.__editorview = self.EDITOR_VIEW(*args, **kwargs)
            self.__editorview.boss = self.boss
            self.__editorview.connect('removed', self.cb_editorview_closed)
            self.__editorview.connect("action", self.__cb_editorview_action)
            self.boss.command(self.PARENT_VIEW,
                              'add-page', contentview=self.__editorview)
        self.__editorview.raise_tab()

    def display_editorpage(self, name):
        self.__editorview.display_page(name)

    def cb_editorview_closed(self, view):
        assert(view is self.__editorview)
        self.__editorview.destroy()
        self.__editorview = None
        view.emit_stop_by_name('removed')

    def __cb_editorview_action(self, view, name):
        self.cb_view_action(view, name)
        view.emit_stop_by_name('action')

    def cb_editorview_action(self, view, name):
        pass

    def get_editor(self):
        return self.__editorview
    editorview = property(get_editor)

class ServiceWithSingleView(Service, ServiceWithEditorMixin):


    def populate_base(self):
        Service.populate_base(self)
        ServiceWithEditorMixin.populate_base(self)

class ServiceWithListedTab(ServiceWithSingleView):

    def create_editorview(self, *args, **kwargs):
        ServiceWithSingleView.create_editorview(self, *args, **kwargs)
        self.editorview.tab.connect('reverted', self.cb_reverted)
        self.editorview.tab.connect('closed', self.cb_closed)

    def cb_closed(self):
        raise NotImplementedError

    def cb_reverted(self):
        self.reload()
        self.editorview.reset()

    def reload(self):
        pass


class GuiServiceWithListedTab(GuiService, ServiceWithListedTab):

    def populate_base(self):
        GuiService.populate_base(self)
        ServiceWithListedTab.populate_base(self)



