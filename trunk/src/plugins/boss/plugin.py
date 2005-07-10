# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 George Cristian Bîrzan gcbirzan@wolfheart.ro

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

import os
import gtk
import logging

import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.configuration.registry as registry

class Plugin(plugin.Plugin):
    NAME = "Boss"
    VISIBLE = False
    
    def configure(self, reg):
        self.ftregistry = reg.add_group('filetypes',
            'Determines which plugins are displayed for which filetypes.')
        self.ftregistry.add('all',
            registry.RegistryItem,
            'project, pastebin',
            'What plugins to always use (comma separated)')
        self.ftregistry.add('python',
            registry.RegistryItem,
            'python_browser, python_debugger, python_profiler',
            'What plugins to use only for python files (comma separated)')
        self.ftregistry.add('None',
            registry.RegistryItem,
            'gazpacho',
            'What plugins to use on unknown files (comma separated)')

        self.plugregistry = reg.add_group('plugins',
            'Determines which plugins are loaded at startup.')
    
        for pluginname in self.prop_optional_pluginlist:
            self.plugregistry.add(pluginname,
                registry.Boolean,
                True,
                'Whether %s wil be loaded at startup (requires restart).' % \
                    pluginname)

    def do_init(self):
        self.filetypes = {}
        self.filetype_triggered = False
        self.filetype_current = 'None'

        self.log = logging.getLogger()
        logging.basicConfig()

    def evt_reset(self):
        self.log.setLevel(self.prop_main_registry.log.level.value())
        
    def evt_bufferchange(self, buffernumber, buffername):
        if not self.filetype_triggered:
            self.filetypes[buffernumber] = 'None'
        if self.filetype_current != self.filetypes[buffernumber]:
            self.filetype_current = self.filetypes[buffernumber]
            self.cb.mainwindow.add_pages(self.get_pluginnames(self.filetype_current))
        self.filetype_triggered = False
        
    def evt_filetype(self, buffernumber, filetype):
        self.do_log_debug('filetype')
        self.filetype_triggered = True
        self.filetypes[buffernumber] = filetype

    def get_pluginnames(self, filetype):
        genplugins = [s.strip() for s in self.ftregistry.all.value().split(',')]
        try:
            ftplugins = [s.strip() for s in self.cb.opts.get('filetypes', filetype).split(',')]
        except AttributeError:
            # No filetypes for the plugin
            ftplugins = []
        return genplugins + ftplugins

    def get_named_plugin(self, name):
        for plugin in self.plugins:
            if plugin.NAME == name:
                return plugin

    def action_log(self, source, message, level):
        """
        Log a message.
        """
        msg = '%s: %s' % (source, message)
        self.log.log(level, msg)

    def action_newterminal(self, command, args, icon, **kw):
        """
        Start a new terminal
        """

    def action_newbrowser(self, url):
        """
        Start a new browser
        """


