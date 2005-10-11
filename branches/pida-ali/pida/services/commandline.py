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
import sys
import optparse

import pida.core.service as service

class Commandline(service.Service):
    """Service for handling command-line arguments."""
    NAME = 'commandline'
    def init(self):
        op = optparse.OptionParser()
        op.add_option('-f', '--registry-file', type='string', nargs=1,
                      action='store')
        op.add_option('-o', '--option', type='string', nargs=1,
                      action='append')
        self.__optparser = op
        self.__opts, self.__args = op.parse_args()

    def get_positional_args(self):
        """Get a list of the positional arguments supplied."""
        return self.__args

    def get_config_options(self):
        """Generator of the command line option arguments."""
        if self.__opts.option:
            for opt in self.__opts.option:
                try:
                    k, v = opt.split('=')
                    yield k, v
                except:
                    self.log_warn('Bad commandline option: %s.' % opt)
                    continue

Service = Commandline
