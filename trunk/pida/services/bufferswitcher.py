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


from pida.core.service import service
from pida.core import actions

class BufferSwitcher(service):
    
    """Just a bag for some key bindings really"""

    def _switch_index(self, index):
        self.boss.call_command('buffermanager', 'switch_index',
                               index=index)

    @actions.action(label='Buffer 1',
                    default_accel='<Alt>1')
    def act_1_buffer(self, action):
        self._switch_index(1)

    @actions.action(label='Buffer 2',
                    default_accel='<Alt>2')
    def act_2_buffer(self, action):
        self._switch_index(2)

    @actions.action(label='Buffer 3',
                    default_accel='<Alt>3')
    def act_3_buffer(self, action):
        self._switch_index(3)

    @actions.action(label='Buffer 4',
                    default_accel='<Alt>4')
    def act_4_buffer(self, action):
        self._switch_index(4)

    @actions.action(label='Buffer 5',
                    default_accel='<Alt>5')
    def act_5_buffer(self, action):
        self._switch_index(5)

    @actions.action(label='Buffer 6',
                    default_accel='<Alt>6')
    def act_6_buffer(self, action):
        self._switch_index(6)

    @actions.action(label='Buffer 7',
                    default_accel='<Alt>7')
    def act_7_buffer(self, action):
        self._switch_index(7)

    @actions.action(label='Buffer 8',
                    default_accel='<Alt>8')
    def act_8_buffer(self, action):
        self._switch_index(8)

    @actions.action(label='Buffer 9',
                    default_accel='<Alt>9')
    def act_9_buffer(self, action):
        self._switch_index(9)

    @actions.action(label='Buffer 10',
                    default_accel='<Alt>0')
    def act_10_buffer(self, action):
        self._switch_index(10)

    def get_menu_definition(self):
        return """<menubar />"""

Service = BufferSwitcher
