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

import pida.core.service as service
import pida.pidagtk.listedtab as listedtab
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.toolbar as toolbar
import pida.core.registry as registry

import os
import os.path

REG_KEY = 'scripts'
REG_DOC = 'The scripts for this context'

REGISTRY_SCHEMA = [(REG_KEY, REG_DOC, '', registry.RegistryItem)]

CONTEXTS = [('file', 'When an action is in the context of a single file')]

CONTEXTS_CONF = os.path.join(os.path.expanduser("~"), ".pida2", "conf", "contexts.conf")

class Context(object):
    scripts = None

class Contexts(service.Service):

    NAME = 'contexts'
    COMMANDS = [('get-toolbar', [('contextname', True)]),
                ('show-editor', [])]
    OPTIONS = [('filename', 'The contexts file.',
                CONTEXTS_CONF, registry.File)]

    def init(self):
        self.__registry = registry.Registry()
        self.__filename = None

    def cmd_get_toolbar(self, contextname, globaldict={}):
        group = self.__registry.get_group(contextname)
        if group is not None:
            tb = toolbar.Toolbar()
            scripts = group.get('scripts').value().split(',')
            scripts = [script.strip() for script in scripts]
            def clicked(clickedtb, name):
                self.boss.command('scripts', 'execute', scriptname=name,
                                  globaldict=globaldict)
            tb.connect('clicked', clicked)
            for script in scripts:
                print script
                tb.add_button(script, script, 'run this')
            return tb

    def reset(self):
        if self.registry_filename != self.__filename:
            self.__filename = self.registry_filename
            if os.path.exists(self.__filename):
                groupdocs = dict(CONTEXTS)
                self.__registry.load_file_with_schema(
                    self.__filename, REGISTRY_SCHEMA, groupdocs)
            else:
                self.__registry.filename= self.__filename
                for context, doc in CONTEXTS:
                    group = self.__registry.add_group(context, doc)
                    opt = group.add(*REGISTRY_SCHEMA[0])
                    opt.setdefault()
                self.__registry.save()
    
    def __adapt_registry(self):
        for group in self.__registry.iter_groups():
            p = Context()
            p.name = group._name
            p.scripts = group.get('scripts').value().split(',')
            yield p

    def __get_registry_filename(self):
        return self.options.get('filename').value()
    registry_filename = property(__get_registry_filename)

    def populate(self):
        self.boss.command('topbar', 'add-button', icon='contexts',
                          tooltip='edit the shortcut contexts',
                          callback=self.cb_show_editor)

    def cmd_show_editor(self):
        self.__view = contentbook.ContentView()
        self.__tab = listedtab.ListedTab(self.__registry)
        self.__view.pack_start(self.__tab)
        self.boss.command('viewbook', 'add-page', contentview=self.__view)

    def cb_show_editor(self, button):
        self.cmd_show_editor()

Service = Contexts
