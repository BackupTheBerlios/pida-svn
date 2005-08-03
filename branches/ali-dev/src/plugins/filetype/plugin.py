# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# $Id: plugin.py 479 2005-08-02 11:39:28Z aafshar $
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

import os
import gtk
import pango
import gobject
import pida.configuration.registry as registry
import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.base as base

class Plugin(plugin.Plugin):
    NAME = 'filetype'

    def do_init(self):
        self.filetypes = {}
        self.filetype_triggered = False
        self.filetype_current = 'None'

    def configure(self, reg):
        self.ftregistry = reg.add_group('filetypes',
            'Determines which plugins are displayed for which filetypes.')
        self.ftregistry.add('all',
            registry.RegistryItem,
            'project, pastebin, gazpacho',
            'What plugins to always use (comma separated)')
        self.ftregistry.add('python',
            registry.RegistryItem,
            'python_browser, python_debugger, python_profiler',
            'What plugins to use only for python files (comma separated)')
        self.ftregistry.add('None',
            registry.RegistryItem,
            '',
            'What plugins to use on unknown files (comma separated)')

        self.plugregistry = reg.add_group('plugins',
            'Determines which plugins are loaded at startup.')
    
        for pluginname in self.prop_optional_pluginlist:
            self.plugregistry.add(pluginname,
                registry.Boolean,
                True,
                'Whether %s wil be loaded at startup (requires restart).' % \
                    pluginname)

    def evt_bufferchange(self, buffernumber, buffername):
        if not self.filetype_triggered:
            self.filetypes[buffernumber] = 'None'
        if self.filetype_current != self.filetypes[buffernumber]:
            self.filetype_current = self.filetypes[buffernumber]
            self.pida.mainwindow.add_pages(self.get_pluginnames(self.filetype_current))
        self.filetype_triggered = False
        self.pida.mainwindow.set_title('PIDA %s' % buffername)
        
    def evt_filetype(self, buffernumber, filetype):
        self.filetype_triggered = True
        self.filetypes[buffernumber] = filetype

    def get_pluginnames(self, filetype):
        genplugins = [s.strip() for s in self.ftregistry.all.value().split(',')]
        ftplugins = []
        if hasattr(self.prop_main_registry.filetypes, filetype):
            fl = getattr(self.prop_main_registry.filetypes, filetype).value()
            ftplugins = [s.strip() for s in fl.split(',')]
            # No filetypes for the plugin
        return genplugins + ftplugins

    def get_named_plugin(self, name):
        for plugin in self.plugins:
            if plugin.NAME == name:
                return plugin

  

