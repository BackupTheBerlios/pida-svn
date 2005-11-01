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

# Core components
import log
import window
import editor
import events
import plugins
import commands
import configmanager
import services


class Boss(object):
    """ The object in charge of everything """
    
    def __init__(self):
        # Set the pidaobject base
        base.pidaobject.boss = self

    def start(self):
        """Start Pida."""
        self.__init()
        self.__bind()
        self.__populate()
        self.__reset()
        self.command('editor', 'start-editor')

    def stop(self):
        self.__editor.stop()
        self.__plugins.stop()
        self.__services.stop()
        self.application.stop()

    def register_command_group(self, name):
        """Register a top-level command group."""
        return self.__commands.add_group(name)

    def register_command(self, group, name, command):
        """Register a command."""

    def register_option_group(self, name, doc):
        """Register and return top-level option group."""
        return self.__config.add_group(name, doc)

    def register_option(seif, group, name, option):
        """Register a configuration option."""

    def register_event_group(self, name):
        """Register a group of events."""
        return self.__events.add_group(name)
    
    def bind_event(self, groupname, name, callback):
        group = self.__events.get(groupname)
        if not group is None:
            group.register(name, callback)

    def command(self, groupname, name, **kw):
        """Call the named command with the keyword arguments."""
        group = self.__commands.get(groupname)
        if group:
            command = group.get(name)
            if command:
                self.log_debug('CMD', 'calling - %s: %s' % (groupname, name))
                return command(**kw)
            else:
                self.log_warn('CMD', 'Command not found: (%s, %s)' % 
                    (groupname, name))
                return
        else:
            self.log_warn('CMD', 'Command not found: (%s, %s)' % 
                           (groupname, name))
            return

    
    def option(self, groupname, name):
        """Get the option value for the grouped named option."""
        return self.__config.get_value(groupname, name)

    def get_command(self, name):
        """Get the named command."""

    def __get_commands(self):
        return self.__commands
    commands = property(__get_commands)

    def get_service(self, name):
        """Get the named service."""
        return self.__services.get(name)

    def get_editor(self):
        return self.__editor

    def get_plugins(self):
        return self.__plugins
    plugins = property(get_plugins)

    def get_main_window(self):
        return self.__window.view

    def get_commandline_args(self):
        """Return the command line arguments Pida was passed."""

    def log_debug(self, source, message):
        """Log a debug message to the log."""
        self.__log.debug(source, message)

    def log_info(self, source, message):
        """Log an info message to the log."""

    def log_warn(self, source, message):
        """Log a warning message to the log."""
        self.__log.warn(source, message)

    def log_error(self, source, message):
        """Log an error message to the log."""

    def __init(self):
        """Initialise components."""
        self.__init_logging()
        self.log_debug('Boss', 'init()')
        self.__init_commands()
        self.__init_config()
        # Can only use the log once it has been started
        self.__init_events()
        self.__init_window()
        self.__init_services()
        self.__init_editor()
        self.__init_plugins()
        self.__load_config()

    def __init_config(self):
        """Initialize the registry."""
        self.__config = configmanager.ConfigManager()

    def __load_config(self):
        """Populate the registry."""
        self.__config.load()

    def __init_logging(self):
        """Initialize the logger."""
        self.__log = log.Log()
        self.log_debug('Boss', 'Logger is up.')

    def __init_commands(self):
        """Initialize the command registry."""
        self.__commands = commands.CommandManager('pida')
        self.log_debug('Boss', 'Command Manager is up.')

    def __init_events(self):
        """Initialise the event registry."""
        self.__events = events.EventManager('pida')
        self.log_debug('Boss', 'EventManager is up.')

    def __init_services(self):
        """Initialise the services."""
        self.__services = services.ServiceManager('pida')
        self.__services.load_all()
        self.log_debug('Boss', 'init_services()')

    def __init_editor(self):
        """Initialise the editor."""
        self.__editor = self.get_service('editormanager')

    def __init_plugins(self):
        """Initialise the plugin manager."""
        self.__plugins = plugins.PluginManager('pida')
        self.__plugins.load_all()
        self.log_debug('Boss', 'PluginManager is up.')

    def __init_window(self):
        """Initialise the main window."""
        self.__window = window.WindowManager()

    def __init_registry_again(self):
        """Reload the full registry."""

    def __bind(self):
        """Bind the events"""
        self.log_debug('Boss', 'bind()')
        self.__editor.bind()
        self.__services.bind()
        self.__plugins.bind()

    def __bind_services_events(self):
        """Bind events in the services."""

    def __bind_editor_events(self):
        """Bind events in the editor."""

    def __bind_plugin_events(self):
        """Bind events in the plugins."""

    def __populate(self):
        """Populate the UI."""
        self.log_debug('Boss', 'populate()')
        self.__config.populate()
        self.__populate_services()
        self.__populate_editor()
        self.__populate_plugins()
        self.__populate_window()

    def __populate_services(self):
        """Populate the services UI."""
        self.__services.populate()

    def __populate_editor(self):
        """Populate the editor UI."""
        self.__editor.populate()

    def __populate_plugins(self):
        """Populate the plugins UI."""
        self.__plugins.populate()

    def __populate_window(self):
        """Populate the window UI."""
        self.__window.populate()

    def __reset(self):
        """Reset live configuration options."""
        self.log_debug('Boss', 'reset()')
        self.__reset_window()
        self.__reset_services()
        self.__reset_plugins()
    reset = __reset

    def __reset_services(self):
        """Reset the services live configuration options."""
        self.__services.reset()

    def __reset_editor(self):
        """Reset the editor live configuration options."""

    def __reset_plugins(self):
        """Reset the services live configuration options."""
        self.__plugins.reset()

    def __reset_window(self):
        """Reset the window."""
        self.__window.reset()


import unittest

class test_boss(unittest.TestCase):

    def test_init(self):
        b = Boss()
        b.init()

if __name__ == '__main__':
    b = Boss()
    b.start()
