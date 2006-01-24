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

import pida.core.service as service

import pida.pidagtk.contentview as contentview
import pida.pidagtk.tree as tree


class service_viewer(contentview.content_view):

    ICON_NAME = 'manhole'
    LONG_TITLE = 'Service diagnostics'

    def init(self):
        boss = self.service.boss
        self.__list = tree.Tree()
        self.widget.pack_start(self.__list)
        self.__list.set_property('markup-format-string',
            '%(name)s')
        self.__list.connect('clicked', self.cb_service_clicked)
#        self.__list.connect('double-clicked', self.cb_paste_db_clicked)
#        self.__list.connect('middle-clicked', self.cb_paste_m_clicked)
        self.__list.connect('right-clicked', self.cb_service_r_clicked)
        for svc in boss.services:
            class si(object):
                def __init__(self, name):
                    self.name = name
                    self.key = name
            svcitem = si(svc.NAME)
            svciter = self.__list.add_item(svcitem)
            cmditer = self.__list.add_item(si('commands'), None, svciter)
            for command in svc.commands:
                citem = si(command.name)
                self.__list.add_item(citem, None, cmditer)
            optiter = self.__list.add_item(si('options'), None, svciter)
            for og in svc.options:
                ogiter = self.__list.add_item(si(og.name), None, optiter)
                for opt in og:
                    oitem = si('%s = %s' % (opt.name, opt.value))
                    self.__list.add_item(oitem, None, ogiter)
            eiter = self.__list.add_item(si('events'), None, svciter)
            for event in svc.events.list_events():
                eitem = si(event)
                self.__list.add_item(eitem, None, cmditer)
            
    def cb_service_r_clicked(self, service, tree_item, event):
        menu = gtk.Menu()
        sensitives = (tree_item is not None)
        for action in ['servicediagnostics+start_service',
                       'servicediagnostics+reset_service',
                       'servicediagnostics+stop_service']:
            if action is None:
                menu.append(gtk.SeparatorMenuItem())
            else:
                act = self.service.action_group.get_action(action)
                if 'new_paste' not in action:
                    act.set_sensitive(sensitives)
                mi = gtk.ImageMenuItem()
                act.connect_proxy(mi)
                mi.show()
                menu.append(mi)
        menu.show_all() 
        menu.popup(None, None, None, event.button, event.time)

    def cb_service_clicked(self,tree,tree_item):
        '''Callback function called when an item is selected in the
        TreeView'''
        self.__tree_selected = \
        self.service.boss.get_service(tree_item.value.name)

    def start_current_service(self):
        self.__tree_selected.start()

    def reset_current_service(self):
        self.__tree_selected.reset()

    def stop_current_service(self):
        self.__tree_selected.stop()


class service_diagnostics(service.service):

    single_view_type = service_viewer
    single_view_book = 'view'

    def cmd_view(self):
        view = self.create_single_view()

    def act_services(self, action):
        self.call('view')

    def act_start_service(self, action):
        self.single_view.start_current_service()

    def act_stop_service(self,action):
        self.single_view.stop_current_service()
    
    def act_reset_service(self,action):
        self.single_view.reset_current_service()

    def get_menu_definition(self):
        return """
               <menubar>
                <menu name="base_tools" action="base_tools_menu">
                <menuitem name="svcd" action="servicediagnostics+services" />
                </menu>
                </menubar>
               """


Service = service_diagnostics




