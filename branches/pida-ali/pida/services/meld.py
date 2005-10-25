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

import pida.pidagtk.contentbook as contentbook
import pida.core.service as service


import sys
sys.path += [ "/usr/lib/meld"
]


import paths
import gettext
import locale

try:
    locale.setlocale(locale.LC_ALL, '')
    gettext.bindtextdomain("meld", paths.locale_dir() )
    gettext.textdomain("meld")
    gettext.install("meld", paths.locale_dir(), unicode=1)
except (IOError,locale.Error), e:
    # fake gettext until translations in place
    print "(meld): WARNING **: %s" % e
    #__builtins__.__dict__["_"] = lambda x : x

#try:
#    __builtins__.__dict__["ngettext"] = gettext.ngettext
#except AttributeError: # python2.2 does not have ngettext
#    __builtins__.__dict__["ngettext"] = \
#        lambda singular, plural, number: _((singular,plural)[number!=1])

import meldapp
import gnomeglade
import task
import svnview



class MeldApp(meldapp.MeldApp):
    #
    def __init__(self):
        gladefile = paths.share_dir("glade2/meldapp.glade")
        gnomeglade.GnomeApp.__init__(self, "meld", '1', gladefile, "meldapp")
        self._map_widgets_into_lists( "settings_drawstyle".split() )
        self.statusbar = meldapp.MeldStatusBar(self.task_progress, self.task_status, self.doc_status)
        self.prefs = meldapp.MeldPreferences()
        if not 1:#hide magic testing button
            self.toolbar_magic.hide()
        elif 1:
            def showPrefs(): meldapp.PreferencesDialog(self)
            #gtk.idle_add(showPrefs)
        self.toolbar.set_style( self.prefs.get_toolbar_style() )
        self.prefs.notify_add(self.on_preference_changed)
        self.idle_hooked = 0
        self.scheduler = task.LifoScheduler()
        self.scheduler.connect("runnable", self.on_scheduler_runnable )
        self.widget.set_default_size(self.prefs.window_size_x, self.prefs.window_size_y)
        self.widget.show()
        print sys.argv
        


import sys

class MeldView(contentbook.ContentView):
    
    def populate(self):
        self.__meld = meldapp.MeldApp()
        #self.__meld.widget.hide()
        #cont = self.__meld.widget.get_children()[0]
        #self.__meld.widget.remove(cont)
        #self.pack_start(cont)
        #cont.show_all()
        #nb = cont.get_children()[0].get_children()[-1].get_children()[0]
        #print nb.get_children()
        #self.nb = nb

    def get_app(self):
        return self.__meld
    app = property(get_app)


import os
        
F = ("/home/ali/working/pida/pida/branches/pida-ali/pida/core/application.py")

import pida.core.buffer as buffer

class MeldBuffer(buffer.TemporaryBuffer):
    
    def get_markup(self):
        return "meld"
    markup = property(get_markup)

class Meld(service.Service):

    NAME = 'meld'
    COMMANDS = [('diff-files', [('filename', True)])]

    def cmd_diff_files(self, filename):
        """docstring"""
        self.view =  MeldView()
        self.view.app.append_diff([filename, F])
        self.boss.command('buffermanager', 'add-buffer',
            buffer=MeldBuffer('meld', ':meld'))
        #difftab = view.nb.get_children()[0]
        #difftab.get_children()[1].hide()
        #difftab.get_children()[2].hide()
        #view.nb.remove(difftab)
        #view.pack_start(difftab)

    def open_file(self, filename):
        self.view.app.widget.present()

    def populate(self):
        self.boss.command('buffermanager', 'register-file-handler',
                           filetype="*:meld", handler=self)
        

Service = Meld
