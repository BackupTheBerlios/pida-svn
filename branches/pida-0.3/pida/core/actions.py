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

import gtk

import base

class action_handler(base.pidacomponent):

    type_name = 'action-handler'

    def __init__(self, service):
        self.__service = service
        self.__init_actiongroup()
        self.init()

    def init(self):
        pass

    def __init_actiongroup(self):
        agname = '%s+%s' % (self.__service.NAME, self.type_name)
        self.__action_group = gtk.ActionGroup(agname)
        for attr in dir(self):
            if attr.startswith('act_'):
                name = attr[4:]
                actname = '%s+%s' % (agname, name)
                words = [(s[0].upper() + s[1:]) for s in name.split('_')]
                label = ' '.join(words)
                stock_id = 'gtk-%s%s' % (words[0][0].lower(), words[0][1:])
                func = getattr(self, attr)
                doc = func.func_doc
                action = gtk.Action(actname, label, doc, stock_id)
                action.connect('activate', func)
                self.__action_group.add_action(action)

    def get_action_group(self):
        return self.__action_group
    action_group = property(get_action_group)

    def get_service(self):
        return self.__service
    service = property(get_service)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                </menu>
                <menu name="base_project" action="base_project_menu">
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                """
