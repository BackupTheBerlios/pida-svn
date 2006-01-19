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

import pida.pidagtk.contentview as contentview
import pida.core.service as service

defs = service.definitions
types = service.types


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
class MeldView(contentview.content_view):

    HAS_DETACH_BUTTON = False
    
    def __bar_from_dock(self, dock):
        return dock.get_children()[0].get_children()[-1].get_children()

    def __nb_from_window(self, window):
        return window.get_children()[0].get_children()[0].get_children()

    def init(self):
        self.__meld = meldapp.MeldApp()
        self.__meld.widget.hide()
        mdock, tdock, cont = self.__nb_from_window(self.__meld.widget)
        menubar = self.__bar_from_dock(mdock)[0]
        toolbar = self.__bar_from_dock(tdock)
        b = gtk.VBox()
        self.widget.pack_start(b)
        cont.reparent(b)
        hidden = gtk.VBox()
        cont.get_children()[-1].reparent(hidden)
        self.__toolbutttons = {}
        for button in toolbar:
            if hasattr(button, 'get_label'):
                label = button.get_label()
                if label in TBMAP:
                    name, icon, tooltip = TBMAP[label]
                    #self.add_button(name, icon, tooltip)
                    self.__toolbutttons[name] = button
        for item in menubar.get_children():
            l = item.get_children()[0]
            text = l.get_text()
            if text == 'File':
                text = 'Meld'
            l.set_markup('<span size="small">%s</span>' % text.lower())
        menuholder = gtk.Alignment()
        #self.menu_area.pack_start(menuholder, expand=False)
        #menubar.reparent(menuholder)

    def cb_toolbar_clicked(self, toolbar, name):
        self.__toolbutttons[name].emit('clicked')

    def get_app(self):
        return self.__meld
    app = property(get_app)

    def view(self, path):
        if os.path.isdir(path):
            self.view_dir(path)
            return True
        elif os.path.exists(path):
            self.view_diff(path)
            return True
        else:
            self.service.log.info('file does not exist %s', path)
            return False

    def view_diff(self, filename):
        app = self.__meld
        doc = vcview.VcView(app.prefs)
        def cleanup():
            app.scheduler.remove_scheduler(doc.scheduler)
        app.scheduler.add_task(cleanup)
        app.scheduler.add_scheduler(doc.scheduler)
        doc.set_location( os.path.dirname(filename) )
        doc.connect("create-diff", lambda obj,arg: app.append_diff(arg) )
        doc.run_diff([filename])

    def view_dir(self, directory):
        app = self.__meld
        app.append_vcview( [directory] )



import os
        
F = ("/home/ali/working/pida/pida/branches/pida-ali/pida/core/application.py")

import pida.core.document as document

class MeldBuffer(document.dummyfile_document):

    PREFIX = 'file-diff'

    ICON_NAME = 'meld'

    markup_prefix = 'dv'
    markup_directory_colour = '#00c000'
    markup_attributes = ['actual_filename', 'markup_directory_colour']
    markup_string = ('<span color="%(markup_directory_colour)s">diff</span>/'
                     '<b>%(actual_filename)s</b>')

    def get_actual_filename(self):
        return os.path.normpath(self.filename.rsplit(':', 1)[0])
    actual_filename = property(get_actual_filename)

class MeldDiffBuffer(MeldBuffer):

    PREFIX = 'file-diff'
    contexts = ['file']

class MeldDirBuffer(MeldBuffer):

    PREFIX = 'dir-diff'

class Meld(service.service):

    multi_view_type = MeldView
    multi_view_book = 'edit'
    
    class meld_handler(document.document_handler):

        globs = ['*:meld']

        def create_document(self, filename, document_type):
            document = MeldBuffer(filename, handler=self)
            return document

        def view_document(self, document):
            view = self.service.create_meld_view(document)
            if view is not None:
                success = view.view(document.actual_filename)
                if not success:
                    view.remove()
    def init(self):
        self.__views = {}

    def cmd_diff(self, filename):
        mangled = self.__manglepath(filename)
        self.boss.call_command('buffermanager', 'open_file',
                                filename=mangled)

    cmd_diff_file = cmd_diff

    def cmd_browse(self, directory):
        self.cmd_diff_file(directory)

    def create_meld_view(self, document):
        filename = document.actual_filename
        if filename in self.__views:
            uid = self.__views[filename]
            self.raise_multi_view(uid)
        else:
            view = self.create_multi_view()
            self.__views[filename] = view.unique_id
            return view

    def cb_multi_view_closed(self, view):
        delete_file = None
        for filename, uid in self.__views.iteritems():
            if uid == view.unique_id:
                delete_file = filename
                break
        if delete_file:
            del self.__views[filename]
            self.boss.call_command('buffermanager', 'file_closed',
                              filename=self.__manglepath(filename))

    def __manglepath(self, filename):
        return '%s:meld' % filename

Service = Meld
