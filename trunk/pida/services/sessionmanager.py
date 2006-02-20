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

import os

import gtk
import gobject

from pida.core import service
from pida.core.service import types
from pida.core.service import definitions as defs

def get_documents_from_file(filename):
    f = open(filename, 'r')
    for line in f:
        filename = line.strip()
        yield filename
    f.close()

def save_documents_to_file(documents, filename):
    f = open(filename, 'w')
    for doc in documents.values():
        if not doc.is_new:
            f.write('%s\n' % doc.filename)
    f.close()

class SessionManager(service.service):

    display_name = 'Session Management'

    class sessions(defs.optiongroup):
        """Session management."""
        class automatically_load_last_session(defs.option):
            """Whether the session will be reloaded from closing PIDA."""
            rtype = types.boolean
            default = True
        class start_with_new_file(defs.option):
            """Whether a new file will be opened on startup if none other is
               specified on the command-line on by a session."""
            rtype = types.boolean
            default = True

    def init(self):
        self.__session_loaded = False

    def bnd_editormanager_started(self):
        if not self.__session_loaded:
            self.__session_loaded = True
            docsloaded = 0
            for filename in self.boss.positional_args:
                self.boss.call_command('buffermanager',
                    'open_file', filename=filename, quiet=True)
                docsloaded = docsloaded + 1
            if self.opt('sessions', 'automatically_load_last_session'):
                most_recent = os.path.join(self.boss.pida_home,
                                    'most-recent.session')
                if os.path.exists(most_recent):
                    docsloaded = (docsloaded +
                    self.call('load_session', session_filename=most_recent))
            if not docsloaded and self.opt('sessions',
                                           'start_with_new_file'):
                self.boss.call_command('buffermanager', 'new_file')

    def act_save_session(self, action):
        """Saves the current session"""
        fdialog = gtk.FileChooserDialog('Please select the session file',
                                 parent=self.boss.get_main_window(),
                                 action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                 buttons=(gtk.STOCK_OK,
                                          gtk.RESPONSE_ACCEPT,
                                          gtk.STOCK_CANCEL,
                                          gtk.RESPONSE_REJECT))
        def response(dialog, response):
            if response == gtk.RESPONSE_ACCEPT:
                self.call('save_session',
                          session_filename=dialog.get_filename())
            dialog.destroy()
        fdialog.connect('response', response)
        fdialog.run()

    def act_load_session(self, action):
        """Loads another session"""
        fdialog = gtk.FileChooserDialog('Please select the session file',
                                 parent=self.boss.get_main_window(),
                                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                 buttons=(gtk.STOCK_OK,
                                          gtk.RESPONSE_ACCEPT,
                                          gtk.STOCK_CANCEL,
                                          gtk.RESPONSE_REJECT))
        def response(dialog, response):
            if response == gtk.RESPONSE_ACCEPT:
                self.call('load_session',
                          session_filename=dialog.get_filename())
            dialog.destroy()
        fdialog.connect('response', response)
        fdialog.run()

    def cmd_save_session(self, session_filename):
        f = open(session_filename, 'w')
        docs = self.boss.call_command('buffermanager',
                                      'get_documents')
        save_documents_to_file(docs, session_filename)

    def cmd_load_session(self, session_filename):
        docsloaded = 0
        for filename in get_documents_from_file(session_filename):
            docsloaded = docsloaded + 1
            def _o(filename):
                self.boss.call_command('buffermanager',
                    'open_file', filename=filename, quiet=True)
            gobject.idle_add(_o, filename)
        return docsloaded

    def stop(self):
        most_recent = os.path.join(self.boss.pida_home, 'most-recent.session')
        self.call('save_session', session_filename=most_recent)

    def get_menu_definition(self):
        return  """
                <ui>
                <menubar>
                <menu name="base_file" action="base_file_menu">
                <placeholder name="ExtrasFileMenu">
                <separator />
                <menuitem name="savesess" action="sessionmanager+save_session" />
                <menuitem name="loadsess" action="sessionmanager+load_session" />
                <separator />
                </placeholder>
                </menu>
                </menubar>
                </ui>
                """

Service = SessionManager
