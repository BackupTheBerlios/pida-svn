# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005-2006 The PIDA Project

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

import pida.core.service as service
import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview
import pida.pidagtk.contextwidgets as contextwidgets

from pida.core import actions

defs = service.definitions
types = service.types

class BufferTree(tree.Tree):
    
    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Time Opened','creation_time'),
                      ('File path','filename'),
                      ('File name','basename'),
                      ('Mime Type','mimetype'),
                      ('File Length','length'),
                      ('Project', 'project_name')]

    def __init__(self):
        tree.Tree.__init__(self)
        self.view.set_expander_column(self.view.get_column(1))
        self.set_property('markup-format-string', '%(filename)s')
        self.view.set_enable_search(False)
        def _se(model, column, key, iter):
            val = model.get_value(iter, 1).value
            isnt = not val.basename.startswith(key)
            return isnt
        self.view.set_search_equal_func(_se)
        
    def set_bufferlist(self, bufferlist):
        # naive
        self.set_items(self.__adapt_bufferlist(bufferlist))

    def set_currentbuffer(self, filename):
        self.set_selected(filename)

class BufferView(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = False

    SHORT_TITLE = 'Buffers'

    LONG_TITLE = 'List of open buffers'

    def init(self):
        self.__buffertree = BufferTree()
        self.__buffertree.set_property('markup-format-string',
                                       '%(markup)s')
        self.__buffertree.connect('clicked',
                                  self.service.cb_plugin_view_clicked)
        self.__buffertree.connect('right-clicked',
                                  self.cb_buffertree_right_clicked)
        self.widget.pack_start(self.__buffertree)

    def get_bufferview(self):
        return self.__buffertree
    bufferview = property(get_bufferview)

    def add_document(self, document):
        self.__buffertree.add_item(document, key=document.unique_id)

    def select_next(self):
        self.__buffertree.view.grab_focus()
        ud = gtk.MOVEMENT_DISPLAY_LINES
        self.__buffertree.view.emit('move-cursor', ud, 1)

    def select_previous(self):
        self.__buffertree.view.grab_focus()
        ud = gtk.MOVEMENT_DISPLAY_LINES
        self.__buffertree.view.emit('move-cursor', ud, -1)

    def search(self):
        self.__buffertree.view.grab_focus()
        self.__buffertree.view.emit('start-interactive-search')

    def goto_index(self, index):
        model = self.__buffertree.model
        try:
            key = model[index][1].key
            self.__buffertree.set_selected(key)
        except IndexError:
            pass

    def cb_buffertree_right_clicked(self, tv, item, event):
        if item is not None:
            document = item.value
        else:
            document = None
        self.__popup_buffer(document, event)

    def __popup_buffer(self, document, event):
        if document is None:
            menu = gtk.Menu()
            oact = self.service.action_group.get_action(
                'buffermanager+open_file')
            mi = oact.create_menu_item()
            menu.add(mi)
            nact = self.service.action_group.get_action(
                'buffermanager+new_file')
            mi = nact.create_menu_item()
            menu.add(mi)
            menu.show_all()
        elif document.is_new:
            menu = gtk.Menu()
            sact = document.handler.action_group.get_action('DocumentSaveAs')
            mi = sact.create_menu_item()
            menu.add(mi)
        else:
            menu = self.service.boss.call_command('contexts',
                'get_context_menu', ctxname='file', ctxargs=[document.filename])
            menu.add(gtk.SeparatorMenuItem())
            clact = self.service.action_group.get_action(
                    'buffermanager+close_buffer')
            mi = clact.create_menu_item()
            menu.add(mi)
        menu.show_all()
        menu.popup(None, None, None, event.button, event.time)

class Buffermanager(service.service):
    
    display_name = 'Buffer Management'
    
    #plugin_view_type = BufferView
    class BufferView(defs.View):
        view_type = BufferView
        book_name = 'content'
    

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

    
    class document_changed(defs.event):
        pass

    class document_modified(defs.event):
        pass

    def bnd_editormanager_started(self):
        if not self.__session_loaded:
            self.__session_loaded = True
            for filename in self.boss.positional_args:
                self.call('open_file', filename=filename, quiet=True)
            if self.opt('sessions', 'automatically_load_last_session'):
                most_recent = os.path.join(self.boss.pida_home,
                                    'most-recent.session')
                if os.path.exists(most_recent):
                    self.call('load_session', session_filename=most_recent)
                def _n():
                    if len(self.__documents) == 0 and self.opt('sessions',
                                                       'start_with_new_file'):
                        self.call('new_file')
                gobject.idle_add(_n)

    def init(self):
        self.__currentdocument = None
        self.__documents = {}
        self.__session_loaded = False
        self.__editor = None

    def bind(self):
        self.action_group.get_action('buffermanager+close_buffer').set_sensitive(False)

    @actions.action(stock_id=gtk.STOCK_OPEN, label=None, is_important=True,
                    default_accel='<Shift><Control>o')
    def act_open_file(self, action):
        """Opens a document"""
        chooser = gtk.FileChooserDialog(
                    title='Open a file',
                    parent=self.boss.get_main_window(),
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        def _cb(dlg, response):
            if response == gtk.RESPONSE_ACCEPT:
                filename = chooser.get_filename()
                self.call('open_file', filename=filename)
            chooser.destroy()
        chooser.connect('response', _cb)
        chooser.run()


    @actions.action(stock_id=gtk.STOCK_CLOSE,
                    label='Close Document',
                    default_accel='<Control>w')
    def act_close_buffer(self, action):
        """Close the current buffer."""
        filename = self.__currentdocument.filename
        self.call('close_file', filename=filename)

    @actions.action(stock_id=gtk.STOCK_QUIT, label=None)
    def act_quit_pida(self, action):
        """Quits the application"""
        self.boss.stop()

    @actions.action(stock_id=gtk.STOCK_NEW, label=None,
                    default_accel='<Shift><Control>n')
    def act_new_file(self, action):
        """Creates a document"""
        self.call('new_file')

    @actions.action(stock_id=gtk.STOCK_ADD,
                    label=None,
                    default_accel='<Shift><Control><Alt>n')
    def act_new_file_wizard(self, action):
        """Creates a document from the wizard"""
        self.call('new_file_wizard')

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

    @actions.action(stock_id=gtk.STOCK_GO_FORWARD, label='Next Buffer',
                    default_accel='<Alt>Right')
    def act_next_buffer(self, action):
        """Go to the next buffer in the buffer list"""
        self.plugin_view.select_next()

    @actions.action(stock_id=gtk.STOCK_GO_BACK, label='Previous Buffer',
                    default_accel='<Alt>Left')
    def act_previous_buffer(self, action):
        """Go to the previous buffer in the buffer list."""
        self.plugin_view.select_previous()

    @actions.action(stock_id=gtk.STOCK_FIND, label='Change Buffer',
                    default_accel='<Shift><Control>b')
    def act_interactive_buffer_change(self, action):
        """Interactively search for a buffer name."""
        self.plugin_view.search()

    def _switch_index(self, index):
        self.plugin_view.goto_index(index - 1)

    @actions.action(label='Buffer 1',
                    default_accel='<Alt>1')
    def act_1_buffer(self, action):
        self._switch_index(1)

    @actions.action(label='Buffer 2',
                    default_accel='<Alt>2')
    def act_2_buffer(self, action):
        self._switch_index(2)

    @actions.action(label='Buffer 3',
                    default_accel='<Alt>3')
    def act_3_buffer(self, action):
        self._switch_index(3)

    @actions.action(label='Buffer 4',
                    default_accel='<Alt>4')
    def act_4_buffer(self, action):
        self._switch_index(4)

    @actions.action(label='Buffer 5',
                    default_accel='<Alt>5')
    def act_5_buffer(self, action):
        self._switch_index(5)

    @actions.action(label='Buffer 6',
                    default_accel='<Alt>6')
    def act_6_buffer(self, action):
        self._switch_index(6)

    @actions.action(label='Buffer 7',
                    default_accel='<Alt>7')
    def act_7_buffer(self, action):
        self._switch_index(7)

    @actions.action(label='Buffer 8',
                    default_accel='<Alt>8')
    def act_8_buffer(self, action):
        self._switch_index(8)

    @actions.action(label='Buffer 9',
                    default_accel='<Alt>9')
    def act_9_buffer(self, action):
        self._switch_index(9)

    @actions.action(label='Buffer 10',
                    default_accel='<Alt>0')
    def act_10_buffer(self, action):
        self._switch_index(10)

    def act_buffers(self, action):
        """The buffer part of the view menu."""
        
    def cmd_open_document(self, document):
        if document is not self.__currentdocument:
            if document.unique_id not in self.__documents:
                self.__add_document(document)
            self.__view_document(document)

    def cmd_open_file(self, filename, quiet=False):
        if (len(filename) and (self.__currentdocument is None or
                filename != self.__currentdocument.filename)):
            document = self.__get_filename_document(filename)
            if document is None:
                try:
                    document = self.__open_file(filename)
                except:
                    if not quiet:
                        raise
                    else:
                        document = None
                if document is not None:
                    self.__add_document(document)
            self.__view_document(document)

    def cmd_new_file(self):
        document = self.__new_file()
        self.__add_document(document)
        self.__view_document(document)

    def cmd_save_as(self):
        document = self.__currentdocument
        chooser = gtk.FileChooserDialog(
                    title='Save as file',
                    parent=self.boss.get_main_window(),
                    action=gtk.FILE_CHOOSER_ACTION_SAVE,
                    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        # pygtk 2.6 compatibility
        if hasattr(chooser, 'set_do_overwrite_confirmation'):
            chooser.set_do_overwrite_confirmation(True)
        def _cb(dlg, response):
            if response == gtk.RESPONSE_ACCEPT:
                filename = chooser.get_filename()
                document.filename = filename
                self.boss.call_command('editormanager', 'save_as',
                                        filename=filename)
                def v():
                    self.__set_document_project(document)
                    document.reset_markup()
                    self.__view_document(document)
                gtk.timeout_add(200, v)
            chooser.destroy()
        chooser.connect('response', _cb)
        chooser.run()

    def cmd_new_file_wizard(self):
        self.__new_file_wizard()

    def cmd_open_file_line(self, filename, linenumber):
        self.call('open_file', filename=filename)
        self.editor.call('goto_line', linenumber=linenumber)

    def cmd_close_file(self, filename):
        doc = self.__get_filename_document(filename)
        if doc is not None:
            doc.handler.close_document(doc)

    def cmd_save_session(self, session_filename):
        f = open(session_filename, 'w')
        for doc in self.__documents.values():
            if not doc.is_new:
                f.write('%s\n' % doc.filename)
        f.close()

    def cmd_load_session(self, session_filename):
        f = open(session_filename, 'r')
        for line in f:
            filename = line.strip()
            def _o(filename):
                self.call('open_file', filename=filename, quiet=True)
                print filename
            gobject.idle_add(_o, filename)
        f.close()

    def cmd_file_closed(self, filename):
        doc = self.__get_filename_document(filename)
        if doc is not None:
            self.__remove_document(doc)
        else:
            self.log.warn('attempt to close file not opened %s', filename)

    def cmd_document_closed(self, document):
        self.__remove_document(document)

    def cmd_reset_current_document(self):
        self.__currentdocument.reset()
        self.events.emit('document_modified', document=self.__currentdocument)

    def __get_filename_document(self, filename):
        for uid, doc in self.__documents.iteritems():
            if doc.filename == filename:
                return doc
        
    def __remove_document(self, document):
        del self.__documents[document.unique_id]
        model = self.plugin_view.bufferview.model
        for row in model:
            if row[0] == str(document.unique_id):
                model.remove(row.iter)
        document.handler.action_group.set_visible(False)
        self.__currentdocument = None
        self.action_group.get_action('buffermanager+close_buffer').set_sensitive(False)
        def refresh():
            if self.__currentdocument is None:
                if len(model):
                    self.__view_document(model[0][1].value)
        gtk.idle_add(refresh)

    def __open_file(self, filename):
        document = self.boss.call_command('documenttypes',
                                          'create_document',
                                           filename=filename)
        return document

    def __new_file(self):
        return self.__open_file(None)

    def __new_file_wizard(self):
        self.boss.call_command('newfile', 'create_interactive')
         
    def __add_document(self, document):
        self.__documents[document.unique_id] = document
        self.__set_document_project(document)
        self.plugin_view.add_document(document)

    def __view_document(self, document):
        self.__currentdocument = document
        document.handler.view_document(document)
        self.__disable_all_handlers([document.handler])
        document.handler.action_group.set_sensitive(True)
        document.handler.action_group.set_visible(True)
        if document.is_new:
            self.boss.call_command('languagetypes', 'hide_all_handlers')
        else:
            self.boss.call_command('languagetypes', 'show_handlers',
                                   document=document)
        self.boss.call_command('window', 'update_action_groups')
        if (self.plugin_view.bufferview.get_selected_key()
                != document.unique_id):
            self.plugin_view.bufferview.set_selected(document.unique_id)
        self.action_group.get_action('buffermanager+close_buffer').set_sensitive(True)
        self.events.emit('document_changed', document=document)

    def __set_document_project(self, document):
        proj = self.boss.call_command('projectmanager',
                                      'get_project_for_file',
                                      filename=document.filename)
        document.set_project(proj)


    def __disable_all_handlers(self, handlers=[]):
        for uid, document in self.__documents.iteritems():
            if document.handler not in handlers:
                document.handler.action_group.set_sensitive(False)
                document.handler.action_group.set_visible(False)

    def get_editor(self):
        if self.__editor is None:
            self.__editor = self.get_service('editormanager')
        return self.__editor
    editor = property(get_editor)

    def cb_plugin_view_clicked(self, view, bufitem):
        doc = bufitem.value
        if doc != self.__currentdocument:
            self.__view_document(doc)
    
    def get_menu_definition(self):
        return  """
                <ui>
                <menubar>
                <menu name="base_file" action="base_file_menu">
                <placeholder name="OpenFileMenu">
                <menuitem name="new" action="buffermanager+new_file" />
                <menuitem name="open" action="buffermanager+open_file" />
                <menuitem action="buffermanager+new_file_wizard" />
                <separator />
                </placeholder>
                <placeholder name="SaveFileMenu" />
                <placeholder name="ExtrasFileMenu">
                <separator />
                <menuitem name="savesess" action="buffermanager+save_session" />
                <menuitem name="loadsess" action="buffermanager+load_session" />
                <separator />
                </placeholder>
                <placeholder name="GlobalFileMenu">
                <menuitem action="buffermanager+close_buffer" />
                <separator />
                <menuitem name="quit" action="buffermanager+quit_pida" />
                </placeholder>
                </menu>
                <menu name="base_view" action="base_view_menu">
                <menuitem name="bufnext"
                          action="buffermanager+next_buffer" />
                <menuitem name="bufprev"
                          action="buffermanager+previous_buffer" />
                <separator />
                <menuitem name="bufsrch"
                          action="buffermanager+interactive_buffer_change" />
                <separator />
                </menu>
                </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
                <toolitem name="New" action="buffermanager+new_file" />
                <toolitem name="Open" action="buffermanager+open_file" />
                <separator />
                </placeholder>
                <placeholder name="SaveFileToolbar">
                </placeholder>
                <placeholder name="EditToolbar">
                <toolitem action="buffermanager+close_buffer" />
                </placeholder>
                <placeholder name="ProjectToolbar">
                </placeholder>
                <placeholder name="VcToolbar">
                </placeholder>
                </toolbar>
                </ui>
                """
    def get_buffer_menu(self):
        s = []
        for i in xrange(1, 11):
            s.append('<menuitem action="buffermanager+%s_buffer" />' % i)
        return '\n'.join(s)


    def stop(self):
        most_recent = os.path.join(self.boss.pida_home, 'most-recent.session')
        self.call('save_session', session_filename=most_recent)

    def get_single_view(self):
        return self.get_first_view('BufferView')
    plugin_view = property(get_single_view)





Service = Buffermanager


