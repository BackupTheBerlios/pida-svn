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


import pida.plugin as plugin
import pida.gtkextra as gtkextra
import gazpachembed
import gtk
import os

class Plugin(plugin.Plugin):
    NAME = 'Gazpacho'
    ICON = 'gazpacho'
    DICON = 'run', 'Run Gazpacho user interface designer.'

    def populate_widgets(self):
        self.second_toolbar = gtkextra.Toolbar(self.cb)
        self.add(self.second_toolbar.win, expand=False)

        self.second_toolbar.add_button('cut', self.cb_gazpacho,
            'Cut the selection', ['cut'])
        self.second_toolbar.add_button('copy', self.cb_gazpacho,
            'Copy the selection', ['copy'])
        self.second_toolbar.add_button('paste', self.cb_gazpacho,
            'Paste the selection', ['paste'])
        self.second_toolbar.add_button('delete', self.cb_gazpacho,
            'Paste the selection', ['delete'])
        self.second_toolbar.add_separator()
        self.undo_but = self.second_toolbar.add_button('undo', self.cb_gazpacho,
                                        'Undo the last operation',
                                        ['undo'])
        self.redo_but = self.second_toolbar.add_button('redo', self.cb_gazpacho,
                                        'Redo the last operation',
                                        ['redo'])

        self.holder = gtk.VBox()
        self.add(self.holder)
        self.button = gtk.Button(label='Launch Gazpacho\n\n'
                                       '(user interface designer)')
        self.holder.pack_start(self.button)
        self.button.connect('clicked', self.cb_alternative)


        self.add_button('save', self.cb_gazpacho, 'Save the current file',
                                                  ['save'])
        self.add_button('open', self.cb_gazpacho, 'Open a file',
                                                  ['open'])
        
    def init(self):
        self.gazpacho = None
        self.menu = None

    def cb_alternative(self, *args):
        self.launch()

    def cb_gazpacho(self, button, commandname):
        if self.gazpacho:
            funcname = '_%s_cb' % commandname
            getattr(self.gazpacho.app, funcname)(None)
        else:
            self.message('Gazpacho is not running.\n'
                         'Please start it.')

    def launch(self):
        if not self.gazpacho:
            self.holder.remove(self.button)
            self.gazpacho = gazpachembed.Gazpacho(self.cb)
        self.gazpacho.launch(self.holder)
        if not self.menu:
            self.menu = self.gazpacho.app.menu
            self.cusbar.win.pack_end(self.menu, expand=False)
            self.gazpacho.app.undo_button = self.undo_but
            self.gazpacho.app.redo_button = self.redo_but
            self.gazpacho.app.refresh_undo_and_redo()
    
    def evt_signaledited(self, projectpath, widgetname, signalname,
                         callbackname):
        projectdir, projectfile = os.path.split(projectpath)
        callbackfile = projectfile.replace('.glade', '_callbacks.py')
        callbackfile = os.path.join(projectdir, callbackfile)
        if not os.path.exists(callbackfile):
            print 'nofile'
            f = open(callbackfile, 'w')
            f.write('# pida generated ui file\n')
            f.write('class CallbacksMixin(object):\n')
            f.close()
        
        f = open(callbackfile, 'r')
        foundline = 0
        if callbackname.startswith('<'):
            callbackname = '%s_%s' % (widgetname, signalname.replace('-', '_'))

        for i, line in enumerate(f):
            if line.count(callbackname):
                foundline = i
                break
        f.close()

        
        if not foundline:
            f = open(callbackfile, 'a')
            f.write('\n')
            f.write('    def %s():\n\n' % callbackname)
            f.close()
            self.cb.action_openfile(callbackfile.replace(' ', r'\ '))
            self.cb.action_gotoline('%')
        else:
            if callbackfile != self.filename:
                self.cb.action_openfile(callbackfile.replace(' ', r'\ '))
            print foundline
            self.cb.action_gotoline(foundline+2)
        

        print widgetname, signalname, callbackname

    def evt_bufferchange(self, number, name):
        self.filename = name

    #def evt_started(self, *args):
    #    self.launch()
