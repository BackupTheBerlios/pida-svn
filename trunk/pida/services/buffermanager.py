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

"""The PIDA Buffer manager."""

import gtk
import gobject

from pida.core import actions
from pida.pidagtk.tree import Tree
from pida.pidagtk.contentview import content_view
from pida.core.service import service, definitions as defs


class BufferTree(Tree):
    """Widget for the buffer list"""
    
    SORT_CONTROLS = True
    SORT_AVAILABLE = [('Time Opened','creation_time'),
                      ('File path','filename'),
                      ('File name','basename'),
                      ('Mime Type','mimetype'),
                      ('File Length','length'),
                      ('Project', 'project_name')]

    def __init__(self):
        super(BufferTree, self).__init__()
        self.view.set_expander_column(self.view.get_column(1))
        self.set_property('markup-format-string', '%(filename)s')
        self.view.set_enable_search(False)
        def _se(model, column, key, iter):
            val = model.get_value(iter, 1).value
            isnt = not val.basename.startswith(key)
            return isnt
        self.view.set_search_equal_func(_se)
        

class BufferView(content_view):
    """View for the buffer list."""

    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = False
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = False
    SHORT_TITLE = 'Buffers'
    LONG_TITLE = 'List of open buffers'

    def init(self):
        """Startup"""
        self.__buffertree = BufferTree()
        self.__buffertree.set_property('markup-format-string',
                                       '%(markup)s')
        self.__buffertree.connect('clicked',
                                  self.service.cb_plugin_view_clicked)
        self.__buffertree.connect('right-clicked',
                                  self.cb_buffertree_right_clicked)
        self.widget.pack_start(self.__buffertree)

    def get_bufferview(self):
        """Get the buffer list widget."""
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
            clact = self.service.action_group.get_action(
                    'buffermanager+close_buffer')
            mi = clact.create_menu_item()
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


class Buffermanager(service):
    """The PIDA buffer manager service"""

    # Service basics

    display_name = 'Buffer Management'
    
    # Views

    class BufferView(defs.View):
        """The buffer list view definition"""
        view_type = BufferView
        book_name = 'content'

    # Events

    class document_changed(defs.event):
        """When the user has switched to a different document"""

    class document_modified(defs.event):
        """When the document has been modified"""

    # Life cycle

    def init(self):
        self.__currentdocument = None
        self.__documents = {}

    def bind(self):
        self.action_group.get_action('buffermanager+close_buffer'
                                     ).set_sensitive(False)
        self.plugin_view = self.create_view('BufferView')

    # External interface

    def cmd_open_document(self, document):
        if document is not self.__currentdocument:
            if document.unique_id not in self.__documents:
                self.__add_document(document)
            self.__view_document(document)

    def cmd_open_file(self, filename, quiet=False):
        """
        Open a filename.
        """
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

    def cmd_open_file_line(self, filename, linenumber):
        self.call('open_file', filename=filename)
        self.boss.call_command('editormanager',
                               'goto_line', linenumber=linenumber)

    def cmd_close_document(self, document):
        """
        Close a document.
        """
        document.handler.close_document(document)

    def cmd_close_documents(self, documents):
        """
        Close more than one document.
        """
        def _c():
            self.cmd_close_document(documents.pop())
            return len(documents)
        self.__editor_idle(_c)

    def cmd_close_file(self, filename):
        """
        Close a loaded document by filename.
        """
        doc = self.__get_filename_document(filename)
        if doc is not None:
            self.cmd_close_document(doc)

    def cmd_close_project_documents(self, project_name):
        """
        Close documents in a project.
        """
        document_to_close = []
        for document in self.__documents.values():
            if document.project_name == project_name:
                document_to_close.append(document)
        self.cmd_close_documents(document_to_close)

    def cmd_document_closed(self, document, dorefresh=True):
        """
        Called by an editor when a document has been closed.

        It is unlikely to be required by non-editor services.
        """
        self.__remove_document(document, dorefresh)

    def cmd_file_closed(self, filename):
        """
        Called by an editor when a file has been closed.

        It is unlikely to be required by non-editor services.
        """
        doc = self.__get_filename_document(filename)
        if doc is not None:
            self.__remove_document(doc)
        else:
            self.log.warn('attempt to close file not opened %s', filename)

    def cmd_reset_current_document(self):
        """
        Call to indicate that the contents of the current document have
        changed.
        """
        self.__currentdocument.reset()
        self.events.emit('document_modified', document=self.__currentdocument)

    def cmd_get_documents(self):
        """
        Return the loaded documents.
        """
        return self.__documents

    def cmd_switch_search(self):
        self.plugin_view.search()

    def cmd_switch_next(self):
        self.plugin_view.select_next()

    def cmd_switch_previous(self):
        self.plugin_view.select_previous()

    def cmd_switch_index(self, index):
        self.plugin_view.goto_index(index - 1)
        
    # Private methods

    def __get_filename_document(self, filename):
        for uid, doc in self.__documents.iteritems():
            if doc.filename == filename:
                return doc
        
    def __remove_document(self, document, dorefresh=True):
        del self.__documents[document.unique_id]
        model = self.plugin_view.bufferview.model
        for i, row in enumerate(model):
            if row[0] == str(document.unique_id):
                model.remove(row.iter)
                break
        document.handler.action_group.set_visible(False)
        self.__currentdocument = None
        self.action_group.get_action('buffermanager+close_buffer').set_sensitive(False)
        if dorefresh:
            self.__refresh_view(i)

    def __refresh_view(self, i):
        print 'refreshing'
        if self.__currentdocument is None:
            if len(model):
                if i == len(model):
                    i = i - 1
                try:
                    val = model[i][1].value
                    self.__view_document(val)
                except:
                    pass

    def __editor_idle(self, call, *args):
        # awfule hack but sometimes vim needs awkward delaying
        if self.get_service('editormanager').editor.NAME.startswith('vim'):
            #gobject.timeout_add(200, call, *args)
            gobject.idle_add(call, *args)
        else:
            call(*args)
        

    def __open_file(self, filename):
        document = self.boss.call_command('documenttypes',
                                          'create_document',
                                           filename=filename)
        return document

    def __new_file(self):
        return self.__open_file(None)

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
        print self.__currentdocument

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

    # UI Callbacks

    def cb_plugin_view_clicked(self, view, bufitem):
        doc = bufitem.value
        if doc != self.__currentdocument:
            self.__view_document(doc)

    # UI Actions

    @actions.action(
        stock_id=gtk.STOCK_OPEN,
        label=None,
        is_important=True,
        default_accel='<Shift><Control>o'
    )
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

    @actions.action(stock_id=gtk.STOCK_NEW, label=None,
                    default_accel='<Shift><Control>n')
    def act_new_file(self, action):
        """Creates a document"""
        self.call('new_file')
    
    # UI Definitions

    def get_menu_definition(self):
        return  """
                <ui>
                <menubar>
                <menu name="base_file" action="base_file_menu">
                <placeholder name="OpenFileMenu">
                <menuitem name="new" action="buffermanager+new_file" />
                <menuitem name="open" action="buffermanager+open_file" />
                <separator />
                </placeholder>
                <placeholder name="SaveFileMenu" />
                <placeholder name="ExtrasFileMenu">
                <separator />
                <separator />
                </placeholder>
                <placeholder name="GlobalFileMenu">
                <menuitem action="buffermanager+close_buffer" />
                <separator />
                <menuitem name="quit" action="buffermanager+quit_pida" />
                </placeholder>
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

Service = Buffermanager

