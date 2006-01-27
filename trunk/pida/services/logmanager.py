# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project

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

import pida.core.service as service

defs = service.definitions
types = service.types


class log_manager(service.service):

    dislay_name = 'Log Manager'

    def cmd_open_log(self):
        self.boss.call_command('buffermanager', 'open_file',
            filename=os.path.join(self.boss.pida_home, 'log', 'pida.log'))

    # ui actions

    def act_open_log(self, action):
        self.call('open_log')

    def act_logs(self, action):
        """The PIDA logs."""
        

    def get_menu_definition(self):
        return """
        <menubar>
        <menu name="base_tools" action="base_tools_menu">
        <menu name="base_pida" action="base_pida_menu">
        <separator />
        <menu name="logmen" action="logmanager+logs">
        <menuitem name="logopen" action="logmanager+open_log" />
        </menu>
        </menu>
        </menu>
        </menubar>        
        """

Service = log_manager

