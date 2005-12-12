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

import pida.utils.vc as vc

defs = service.definitions
types = service.types

class version_control(service.service):

    class meld_integration(defs.optiongroup):
        """How much meld will be used."""
        class use_meld_for_statuses(defs.option):
            rtype = types.boolean
            default = True

    def cmd_get_vcs_for_directory(self, directory):
        print directory
        return vc.Vc(directory)

    def cmd_statuses(self, directory):
        if self.opt('meld_integration', 'use_meld_for_statuses'):
            self.boss.call_command('meldembed', 'browse',
                                    directory=directory)
        else:
            print 'not using meld'
        

Service = version_control
