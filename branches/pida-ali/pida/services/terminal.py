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

import pida.core.registry as registry

class TermContent(contentbook.ContentView):
    ICON = 'manhole'
    ICON_TEXT = 'terminal'
    def __init__(self, fd):
        contentbook.ContentView.__init__(self)
        self.__term = pyshell.VteTerm(fd)
        self.pack_start(self.__term)

    def get_term(self):
        return self.__term
    term = property(get_term)

class VtermContent(contentbook.ContentView):
    ICON = 'terminal'
    ICON_TEXT = 'terminal'
    def __init__(self):
        contentbook.ContentView.__init__(self)
        self.__term = pyshell.vte.Terminal()
        self.pack_start(self.__term)

    def fork(self, args, **kw):
        self.__term.fork_command(args[0], args, **kw)
        
    def get_term(self):
        return self.__term
    term = property(get_term)

class TerminalManager(service.Service):

    NAME = 'terminal'
    COMMANDS = [['execute-line',[('commandline', True)]],
                ['execute-py-file',[('filename', True), ('datacallback', True),
                                    ('kwargs', False)]],
                ['execute-py-shell',[]],
                ['execute',[('cmdargs', True),('spkwargs', False)]],
                ['execute-hidden',[('cmdargs', True),('spkwargs', False)]],
                ['execute-vt',[('cmdargs', True),('vtkwargs', False)]],
                ['execute-vt-shell', [('kwargs', False)]]]

    OPTIONS = [('font',
                'The font that will be used in newly started terminals.',
                'Monospace 9', registry.Font),
               ('transparency',
                'Whether newly started terminals will display transparently.',
                False, registry.Boolean),
               ('background-color',
                'The color that will be used to display terminal backgrounds',
                '#000000', registry.Color),
               ('foreground-color',
                'The color that will be used to display terminal foregrounds.',
                '#f0f0f0', registry.Color)]

    def init(self):
        self.__contentpages = []

    def cmd_execute(self, cmdargs, spkwargs={}):
        self.fork_py(cmdargs, **spkwargs)

    def cmd_execute_vt(self, cmdargs, vtkwargs={}):
        self.fork_vt(cmdargs, **vtkwargs)

    def cmd_execute_line(self, commandline):
        self.fork_py(commandline.split())

    def cmd_execute_vt_shell(self, kwargs={}):
        self.fork_vt(['bash'], **kwargs)

    def cmd_execute_py_file(self, filename, **kw):
        self.fork_py(['python', filename], **kw)
        
    def cmd_execute_py_shell(self):
        self.fork_py(['python'], shell=True)

    def cmd_execute_hidden(self, cmdargs, datacallback, kwargs={}):
        p = popen(cmdargs, datacallback, kwargs)

    def fork_py(self, cmdargs, **kw):
        self.__master, slave = pty.openpty()
        self.__console = subprocess.Popen(args=cmdargs, stdin=slave, stdout=slave,
                                          stderr=slave, **kw)
        content = TermContent(self.__master)
        self.__configure_term(content)
        self.boss.command('contentbook', 'add-page', contentview=content)
        
    def fork_vt(self, cmdargs, **kw):
        content = VtermContent()
        self.__configure_term(content)
        content.fork(cmdargs, **kw)
        self.boss.command('viewbook', 'add-page', contentview=content)
        
    def populate(self):
        def vt_shell(button):
            self.cmd_execute_vt_shell()
        self.boss.command('topbar', 'add-button', icon='terminal',
                           tooltip='New shell.', callback=vt_shell)

    def __configure_term(self, content):
        term = content.term
        trans = self.options.get('transparency').value()
        if trans:
            term.set_background_transparent(trans)
        cmap = term.get_colormap()
        c = self.options.get('background-color').value()
        bgcol = cmap.alloc_color(c)
        c = self.options.get('foreground-color').value()
        fgcol = cmap.alloc_color(c)
        term.set_colors(fgcol, bgcol, [])
        font = self.options.get('font').value()
        term.set_font_from_string(font)
        term.set_size(60, 10)
        term.set_size_request(-1, 50)
        self.__connect_term(content)

    def __connect_term(self, content):
        term = content.term
        def title_changed(term):
            title = term.get_window_title()
            content.set_title(title)
        term.connect('window-title-changed', title_changed)


class popen(object):
    
    def __init__(self, cmdargs, callback, kwargs):
        self.__running = False
        self.__readbuf = []
        self.__callback = callback
        self.run(cmdargs, **kwargs)
    
    def run(self, cmdargs, **kwargs):
        console = subprocess.Popen(args=cmdargs, stdout=subprocess.PIPE,
                                                 stderr=subprocess.STDOUT,
                                                 **kwargs)
        self.__running = True
        self.__readtag = gobject.io_add_watch(
            console.stdout, gobject.IO_IN, self.cb_read)
        self.__huptag = gobject.io_add_watch(
            console.stdout, gobject.IO_HUP, self.cb_hup)

    def cb_read(self, fd, cond):
        data = os.read(fd.fileno(), 1024)
        self.__readbuf.append(data)
        return True

    def cb_hup(self, fd, cond):
        self.__callback(''.join(self.__readbuf))
        self.__running = False
        gobject.source_remove(self.__readtag)
        return False


Service = TerminalManager
