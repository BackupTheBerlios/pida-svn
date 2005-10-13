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
import pida.pidagtk.pyshell as pyshell
import pty
import sys
import subprocess
import gobject
import os
class TermContent(contentbook.ContentView):
    def __init__(self, fd):
        contentbook.ContentView.__init__(self)
        self.__term = pyshell.VteTerm(fd)
        self.pack_start(self.__term)

class VtermContent(contentbook.ContentView):
    def __init__(self):
        contentbook.ContentView.__init__(self)
        self.__term = pyshell.vte.Terminal()
        self.pack_start(self.__term)

    def fork(self, args, **kw):
        self.__term.fork_command(args[0], args, **kw)
        

class TerminalManager(service.Service):

    NAME = 'terminal'
    COMMANDS = [['execute-line',[('commandline', True)]],
                ['execute-py-file',[('filename', True), ('datacallback', True),
                                    ('kwargs', False)]],
                ['execute-py-shell',[]],
                ['execute',[('cmdargs', True),('spkwargs', False)]],
                ['execute-hidden',[('cmdargs', True),('spkwargs', False)]],
                ['execute-vt',[('cmdargs', True),('vtkwargs', False)]],
                ['execute-vt-shell',[]]]

    def cmd_execute(self, cmdargs, spkwargs={}):
        self.fork_py(cmdargs, **spkwargs)

    def cmd_execute_vt(self, cmdargs, vtkwargs={}):
        self.fork_vt(cmdargs, **vtkwargs)

    def cmd_execute_line(self, commandline):
        self.fork_py(commandline.split())

    def cmd_execute_vt_shell(self):
        self.fork_vt(['bash'])

    def cmd_execute_py_file(self, filename, **kw):
        self.fork_py(['python', filename], **kw)
        
    def cmd_execute_py_shell(self):
        self.fork_py(['python'], shell=True)

    def cmd_execute_hidden(self, cmdargs, datacallback, kwargs={}):
        readbuf = []
        console = subprocess.Popen(args=cmdargs, stdout=subprocess.PIPE,
                                                 stderr=subprocess.STDOUT,
                                                 **kwargs)
        running = [1]
        def read(fd, cond):
            if cond == gobject.IO_IN:
                data = os.read(fd.fileno(), 1024)
                readbuf.append(data)
                return running == [1]
            elif cond == gobject.IO_HUP:
                datacallback(''.join(readbuf))
                running = False
                return False

        gobject.io_add_watch(console.stdout, gobject.IO_IN, read)
        gobject.io_add_watch(console.stdout, gobject.IO_HUP, read)
        

    def fork_py(self, cmdargs, **kw):
        self.__master, slave = pty.openpty()
        self.__console = subprocess.Popen(args=cmdargs, stdin=slave, stdout=slave,
                                          stderr=slave, **kw)
        content = TermContent(self.__master)
        self.boss.command('contentbook', 'add-page', contentview=content)
        
    def fork_vt(self, cmdargs, **kw):
        content = VtermContent()
        content.fork(cmdargs, **kw)
        self.boss.command('contentbook', 'add-page', contentview=content)
        

class popen(object):
    
    def __init__(self, cmdargs):
        self.__running = False
        self

Service = TerminalManager
