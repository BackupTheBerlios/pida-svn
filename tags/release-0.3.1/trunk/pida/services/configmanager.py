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
from pida.core import actions
import pida.pidagtk.configview as configview

class config_view(configview.config_view):

    ICON_NAME = 'config'

    SHORT_TITLE = 'Configuration'

    LONG_TITLE = 'PIDA configuration manager'

class config_manager(service.service):
    
    single_view_type = config_view
    single_view_book = 'ext'

    def cmd_edit(self):
        regs = [(svc.NAME, svc.options) for svc in self.boss.services]
        view = self.create_single_view()
        view.set_registries(regs)
        view.connect('data-changed', self.cb_view_data_changed)

    def cb_view_data_changed(self, view):
        self.boss.reset()

    @actions.action(stock_id=gtk.STOCK_PREFERENCES, label=None,
                    default_accel='<Shift><Control>k')
    def act_configuration(self, action):
        self.call('edit')

    def get_menu_definition(self):
        return  """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                    <placeholder name="PreferencesMenu">
                        <separator />
                        <menuitem name="confedit" action="configmanager+configuration" />
                    </placeholder>
                </menu>
                <menu name="base_project" action="base_project_menu">
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                """

Service = config_manager

    
