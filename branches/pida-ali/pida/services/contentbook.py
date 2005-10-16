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
import pida.pidagtk.contentbook as contentbook

class Contentbook(service.GuiService):

    NAME = 'contentbook'
    COMMANDS = [['add-page', [('contentview', True)]]]
    VIEW = contentbook.ContentBookInSlider

    def populate(self):
        self.slider = None

    def cmd_add_page(self, contentview):
        self.view.append_page(contentview)

    def toolbar_action_hello(self):
        self.boss.command('manhole', 'run')

    def toolbar_action_hello2(self):
        def p(data):
            self.log_debug('%s' % data)
        self.boss.command('versioncontrol', 'get-statuses',
                           datacallback=p,
                           directory='/home/ali/working/pida/pida/trunk')

    def toolbar_action_hello3(self):
        self.boss.command('filemanager', 'browse',
                           directory='/home/ali/working/pida/pida')

    def reset(self):
        self.view.shrink()


Service = Contentbook
