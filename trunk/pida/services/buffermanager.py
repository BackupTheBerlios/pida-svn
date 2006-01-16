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
#import pida.core.buffer as buffer
import glob
import os
import gtk
import pida.core.service as service
import pida.pidagtk.buffertree as buffertree
import gobject

import pida.pidagtk.contentview as contentview

defs = service.definitions
types = service.types

class BufferView(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = False

    def init(self):
        self.__buffertree = buffertree.BufferTree()
        self.__buffertree.set_property('markup-format-string',
                                       '%(markup)s')
        self.__buffertree.connect('clicked',
                                  self.service.cb_single_view_clicked)
        #self.widget.pack_start(self.__buffertree.details_box, expand=False)
        self.widget.pack_start(self.__buffertree)

    def get_bufferview(self):
        return self.__buffertree
    bufferview = property(get_bufferview)

    def add_document(self, document):
        self.__buffertree.add_item(document, key=document.unique_id)

class Buffermanager(service.service):
    
    display_name = 'Buffer Management'
    
    single_view_type = BufferView

    class sessions(defs.optiongroup):
        class automatically_load_last_session(defs.option):
            rtype = types.boolean
            default = True
    
    class document_changed(defs.event):
        pass

    class document_modified(defs.event):
        pass

    def bnd_editormanager_started(self):
        for filename in self.boss.positional_args:
            self.call('open_file', filename=filename)
        if not self.__session_loaded:
            if self.opt('sessions', 'automatically_load_last_session'):
                most_recent = os.path.join(self.boss.pida_home,
                                       'most-recent.session')
                if os.path.exists(most_recent):
                    self.call('load_session', session_filename=most_recent)
            self.__session_loaded = True
        

    def init(self):
        self.__currentdocument = None
        self.__documents = {}
        self.__filenames = {}
        self.__session_loaded = False
        self.__editor = None

    def bind(self):
        self.create_single_view()

    def act_open_file(self, action):
        self.boss.call_command('filemanager', 'browse')

    def act_quit_pida(self, action):
        self.boss.stop()

    def act_save_session(self, action):
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
        
    def cmd_open_document(self, document):
        if document is not self.__currentdocument:
            if document.unique_id not in self.__filenames:
                self.__add_document(document)
            self.__view_document(document)

    def cmd_open_file(self, filename):
        if (len(filename) and (self.__currentdocument is None or
                filename != self.__currentdocument.filename)):
            filename = os.path.abspath(filename)
            if filename in self.__documents:
                document = self.__documents[filename]
                self.__view_document(document)
                return 'switching'
            else:
                document = self.__open_file(filename)
                self.__add_document(document)
                self.__view_document(document)
                return 'creating'
        else:
            return 'current'

    def cmd_open_file_line(self, filename, linenumber):
        self.call('open_file', filename=filename)
        self.editor.call('revert')
        self.editor.call('goto_line', linenumber=linenumber)

    def cmd_close_file(self, filename):
        if filename in self.__documents:
            doc = self.__documents[filename]
            doc.handler.close_document(doc)

    def cmd_save_session(self, session_filename):
        f = open(session_filename, 'w')
        for filename in self.__documents:
            f.write('%s\n' % filename)
        f.close()

    def cmd_load_session(self, session_filename):
        f = open(session_filename, 'r')
        for line in f:
            filename = line.strip()
            self.call('open_file', filename=filename)
        lines = f.readlines()
        f.close()
        return lines

    def cmd_file_closed(self, filename):
        if filename in self.__documents:
            document = self.__documents[filename]
            self.__remove_document(document)
        else:
            self.log.warn('attempt to close file not opened %s', filename)

    def cmd_reset_current_document(self):
        self.__currentdocument.reset()
        self.events.emit('document_modified', document=self.__currentdocument)
        
    def __remove_document(self, document):
        del self.__filenames[document.unique_id]
        del self.__documents[document.filename]
        model = self.single_view.bufferview.model
        for row in model:
            if row[0] == str(document.unique_id):
                model.remove(row.iter)
        document.handler.action_group.set_visible(False)
        self.__currentdocument = None
            

    def __open_file(self, filename):
        document = self.boss.call_command('documenttypes',
                                          'create_document',
                                           filename=filename)
        return document

    def __add_document(self, document):
        self.__documents[document.filename] = document
        self.__filenames[document.unique_id] = document.filename
        self.single_view.add_document(document)

    def __view_document(self, document):
        self.__currentdocument = document
        document.handler.view_document(document)
        self.__disable_all_handlers()
        document.handler.action_group.set_sensitive(True)
        document.handler.action_group.set_visible(True)
        self.boss.call_command('languagetypes', 'show_handlers',
                               document=document)
        self.boss.call_command('window', 'update_action_groups')
        if (self.single_view.bufferview.get_selected_key()
                != document.unique_id):
            self.single_view.bufferview.set_selected(document.unique_id)
        self.events.emit('document_changed', document=document)

    def __disable_all_handlers(self):
        for filename, document in self.__documents.iteritems():
            document.handler.action_group.set_sensitive(False)
            document.handler.action_group.set_visible(False)

    def get_editor(self):
        if self.__editor is None:
            self.__editor = self.get_service('editormanager')
        return self.__editor
    editor = property(get_editor)

    def cb_single_view_clicked(self, view, bufitem):
        doc = bufitem.value
        if doc != self.__currentdocument:
            self.__view_document(doc)
    
    def get_menu_definition(self):
        return  """
                <ui>
                <menubar>
                <menu name="base_file" action="base_file_menu">
                <placeholder name="OpenFileMenu">
                <menuitem name="open" action="buffermanager+open_file" />
                </placeholder>
                <placeholder name="SaveFileMenu" />
                <placeholder name="ExtrasFileMenu">
                <separator />
                <menuitem name="savesess" action="buffermanager+save_session" />
                <menuitem name="loadsess" action="buffermanager+load_session" />
                <separator />
                </placeholder>
                <placeholder name="GlobalFileMenu">
                <menuitem name="quit" action="buffermanager+quit_pida" />
                </placeholder>
                </menu>
                </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
                <separator />
                <toolitem name="Open" action="buffermanager+open_file" />
                <separator />
                </placeholder>
                <placeholder name="SaveFileToolbar">
                </placeholder>
                <placeholder name="EditToolbar">
                </placeholder>
                <placeholder name="ProjectToolbar">
                </placeholder>
                <placeholder name="VcToolbar">
                </placeholder>
                </toolbar>
                </ui>
                """

    def stop(self):
        most_recent = os.path.join(self.boss.pida_home, 'most-recent.session')
        self.call('save_session', session_filename=most_recent)





Service = Buffermanager


