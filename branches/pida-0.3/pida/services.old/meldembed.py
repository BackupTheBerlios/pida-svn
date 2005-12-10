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
#sys.path += [ "/usr/lib/meld"
#]
# system
import sys
import os

# gnome
import gtk
import gtk.glade
import gobject

# project
#import gnomeglade
#import misc

import gettext
import locale
import meld.paths as paths
sys.path.append(paths.appdir)
try:
    locale.setlocale(locale.LC_ALL, '')
    gettext.bindtextdomain("meld", paths.locale_dir() )
    gettext.textdomain("meld")
    gettext.install("meld", paths.locale_dir(), unicode=1)
except (IOError,locale.Error), e:
    # fake gettext until translations in place
    print "(meld): WARNING **: %s" % e
    __builtins__.__dict__["_"] = lambda x : x
#__builtins__.__dict__["ngettext"] = gettext.ngettext


import meld.meldapp as meldapp
import meld.gnomeglade as gnomeglade
import meld.task as task

import meld.filediff as filediff
import meld.vcview as vcview
import meld.dirdiff as dirdiff

import meld.prefs as prefs


class MeldAppi(meldapp.MeldApp):
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
        

TBMAP = {
    'New...' : ('new', 'new', 'Create a new diff.'),
    'Save' : ('save', 'save', 'Save the current file.'),
    'Undo': ('undo', 'undo', 'Undo the last action.'),
    'Redo': ('redo', 'redo', 'Redo the last action.'),
    'Down': ('down', 'down', 'down'),
    'Up': ('up', 'up', 'up'),
    'Stop': ('stop', 'stop', 'Stop the current process.')
}

import sys
import gtk
class MeldView(contentbook.ContentView):

    HAS_DETACH_BUTTON = False
    
    def __bar_from_dock(self, dock):
        return dock.get_children()[0].get_children()[-1].get_children()

    def __nb_from_window(self, window):
        return window.get_children()[0].get_children()[0].get_children()

    def populate(self):
        self.__meld = meldapp.MeldApp()
        self.__meld.widget.hide()
        mdock, tdock, cont = self.__nb_from_window(self.__meld.widget)
        menubar = self.__bar_from_dock(mdock)[0]
        toolbar = self.__bar_from_dock(tdock)
        b = gtk.VBox()
        self.pack_start(b)
        cont.reparent(b)
        hidden = gtk.VBox()
        cont.get_children()[-1].reparent(hidden)
        self.__toolbutttons = {}
        for button in toolbar:
            if hasattr(button, 'get_label'):
                label = button.get_label()
                if label in TBMAP:
                    name, icon, tooltip = TBMAP[label]
                    self.add_button(name, icon, tooltip)
                    self.__toolbutttons[name] = button
        for item in menubar.get_children():
            l = item.get_children()[0]
            text = l.get_text()
            if text == 'File':
                text = 'Meld'
            l.set_markup('<span size="small">%s</span>' % text.lower())
        menuholder = gtk.Alignment()
        self.menu_area.pack_start(menuholder, expand=False)
        menubar.reparent(menuholder)

    def cb_toolbar_clicked(self, toolbar, name):
        self.__toolbutttons[name].emit('clicked')

    def get_app(self):
        return self.__meld
    app = property(get_app)


import os
        
F = ("/home/ali/working/pida/pida/branches/pida-ali/pida/core/application.py")

import pida.core.buffer as buffer

class MeldBuffer(buffer.DummyBuffer):

    PREFIX = 'file-diff'

    ICON_NAME = 'meld'

    def get_actual_filename(self):
        return os.path.basename(self.filename.rsplit(':', 1)[0])
    actual_filename = property(get_actual_filename)

    def get_markup(self):
        MU = ('<span>'
              '<span foreground="#00a0a0"><tt>'
              '<b>%s </b></tt></span>'
              '<b>%s</b>'
              '</span>')
        return MU % (self.PREFIX, os.path.basename(self.actual_filename))
    markup = property(get_markup)

class MeldDiffBuffer(MeldBuffer):

    PREFIX = 'file-diff'
    contexts = ['file']

class MeldDirBuffer(MeldBuffer):

    PREFIX = 'dir-diff'

class Meld(service.Service):

    NAME = 'meld'
    COMMANDS = [('diff-file', [('filename', True)]),
                ('browse', [('directory', True)])]

    def init(self):
        self.__views = {}

    def cmd_diff_file(self, filename):
        self.__create_view(self.action_diff, filename)

    def cmd_browse(self, directory):
        self.__create_view(self.action_browse, directory)

    def action_browse(self, app, directory):
        app.append_vcview( [directory] )
        return MeldBuffer('%s:meld' % directory)

    def action_diff(self, app, filename):
        doc = vcview.VcView(app.prefs)
        def cleanup():
            app.scheduler.remove_scheduler(doc.scheduler)
        app.scheduler.add_task(cleanup)
        app.scheduler.add_scheduler(doc.scheduler)
        doc.set_location( os.path.dirname(filename) )
        doc.connect("create-diff", lambda obj,arg: app.append_diff(arg) )
        doc.run_diff([filename])
        return MeldBuffer('%s:meld' % filename)

    def __create_view(self, action, path):
        if path in self.__views:
            self.__views[path].raise_tab()
            self.boss.command('buffermanager', 'open-file', filename=path +
                              ':meld')
        else:
            view = MeldView()
            self.__views[path] = view
            view.connect('removed', self.cb_view_removed)
            view.filename = path
            new_buf = action(view.app, path)
            self.boss.command("editor", "add-page",
                               contentview=view)
            new_buf.handler = self
            new_buf.boss = self.boss
            self.boss.command('buffermanager', 'add-buffer',
                buffer=new_buf)
            return view

    def cb_view_removed(self, view):
        del self.__views[view.filename]
        self.boss.command('buffermanager', 'close-file',
                          filename='%s:meld' % view.filename)

    def open_file(self, buf):
        filename = buf.filename.rsplit(':', 1)[0]
        self.__views[filename].raise_tab()

    def populate(self):
        self.boss.command('buffermanager', 'register-file-handler',
                           filetype="*:meld", handler=self)
        

Service = Meld
