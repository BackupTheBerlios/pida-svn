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
import pango
import gobject
import pida.plugin as plugin
import pida.gtkextra as gtkextra
import pida.configuration.registry as registry


class Plugin(plugin.Plugin):
    NAME = "Boss"
    VISIBLE = False
    
    def configure(self, reg):
        self.registry = reg.add_group('boss',
            'Boss configuration options.')
        self.registry.add('all',
            registry.RegistryItem,
            'project, pastebin',
            'What plugins to always use (comma separated)')
        self.registry.add('python',
            registry.RegistryItem,
            'python_browser, python_debugger, python_profiler',
            'What plugins to use only for python files (comma separated)')
        self.registry.add('None',
            registry.RegistryItem,
            'gazpacho',
            'What plugins to use on unknown files (comma separated)')

    def init(self):
        self.filetype_triggered = False
        self.filetypes = dict()
        self.filetype_current = 'None'

    def evt_bufferchange(self, buffernumber, buffername):
        if not self.filetype_triggered:
            self.filetypes[buffernumber] = 'None'
        if self.filetype_current != self.filetypes[buffernumber]:
            self.filetype_current = self.filetypes[buffernumber]
            self.add_pages(self.get_plugins(self.filetype_current))
        self.filetype_triggered = False
        
    def get_plugins(self, filetype):
        plugins = list()
        active_plugins = list()
        
        generic = map(str.strip, self.cb.registry.boss.all.value().split(','))
        try:
            file = map(str.strip, self.cb.opts.get('boss', filetype).split(','))
        except AttributeError:
            file = []
        plugins = [plugin.NAME for plugin in self.cb.plugins]
        return [self.cb.plugins[plugins.index(plugin)] for plugin in generic + file]

    def add_pages(self, plugins):
        for i in xrange(self.cb.mainwindow.notebook.get_n_pages()):
            self.cb.mainwindow.notebook.remove_page(-1)
        for plugin in plugins:
            self.cb.mainwindow.add_opt_plugin(plugin)
        
    def evt_filetype(self, buffernumber, filetype):
        self.filetype_triggered = True
        self.filetypes[buffernumber] = filetype

