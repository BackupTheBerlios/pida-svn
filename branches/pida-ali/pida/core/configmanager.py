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

import service
import registry

import pida.pidagtk.listedtab as listedtab
import pida.pidagtk.contentbook as contentbook

class ConfigManager(service.Service):
    NAME = 'configmanager'

    COMMANDS = [("show-editor", []),
                ("reload", [])]

    def init(self):
        self.__registry = registry.Registry()
        self.__view = None

    def load(self):
        self.__registry.load_file('/home/ali/.pida2/conf/pida.conf')

    def add_group(self, name, doc):
        return self.__registry.add_group(name, doc)

    def get(self, group, name):
        return self.__registry.get(group, name)

    def get_value(self, group, name):
        opt = self.get(group, name)
        if opt:
            return opt.value()

    def cmd_reload(self):
        self.load()

    def cmd_show_editor(self):
        if self.__view is None:
            notebook = listedtab.ListedTab(self.__registry)
            notebook.connect("applied", self.cb_view_applied)
            notebook.connect("closed", self.cb_view_closed)
            self.__view = ConfigEditor()
            self.__view.pack_start(notebook)
            self.boss.command('viewbook', 'add-page', contentview=self.__view)
        else:
            self.__view.raise_tab()

    def populate(self):
        self.boss.command("topbar", "add-button", icon="configure",
                          tooltip="configuration",
                          callback=self.cb_show_editor)

    def cb_show_editor(self, button):
        self.cmd_show_editor()

    def cb_view_closed(self, listedtab):
        self.__view.close()

    def cb_view_applied(self, listedtab):
        self.boss.reset()

class ConfigEditor(contentbook.ContentView):

    ICON = "configure"
    ICON_TEXT = "The pIDA configuration manager"
