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
import gtk
import pida.core.service as service
import pida.core.document as document
from pida.core import actions

types = service.types
defs = service.definitions

import glob
import sre

class document_type_handler(service.service):

    class fallback_handler(defs.document_handler):
        """The fallback buffer creator."""

        globs = None

        def create_document(self, filename, document_type=None, **kw):
            if document_type is None:
                document_type = document.realfile_document
            doc = document_type(filename=filename,
                                         handler=self, **kw)
            return doc

        def view_document(self, document):
            self.service.get_service('editormanager').call('edit',
                                      document=document)

        def close_document(self, document):
            self.service.boss.call_command('editormanager', 'close',
                                            filename=document.filename)

        @actions.action(stock_id=gtk.STOCK_REDO, label=None)
        def act_redo(self, action):
            """Redo the undone action"""
            self.service.boss.call_command('editormanager', 'redo')

        @actions.action(stock_id=gtk.STOCK_UNDO, label=None, is_important=True)
        def act_undo(self, action):
            """Undo the last action"""
            self.service.boss.call_command('editormanager', 'undo')

        @actions.action(stock_id=gtk.STOCK_CUT, label=None)
        def act_cut(self, action):
            """Cut the selection"""
            self.service.boss.call_command('editormanager', 'cut')

        @actions.action(stock_id=gtk.STOCK_COPY, label=None)
        def act_copy(self, action):
            """Copy the selection"""
            self.service.boss.call_command('editormanager', 'copy')

        @actions.action(stock_id=gtk.STOCK_PASTE, label=None)
        def act_paste(self, action):
            """Paste the clipboard"""
            self.service.boss.call_command('editormanager', 'paste')

        @actions.action(stock_id=gtk.STOCK_SAVE,
                        label=None,
                        is_important=True,
                        name="DocumentSave")
        def act_save(self, action):
            """Save the document"""
            self.service.boss.call_command('editormanager', 'save')

        @actions.action(stock_id=gtk.STOCK_REVERT_TO_SAVED, label=None)
        def act_revert(self, action):
            """Reverts a document"""
            self.service.boss.call_command('editormanager', 'revert')

        def get_menu_definition(self):
            return """
                <menubar>
                <menu name="base_file" action="base_file_menu">
                <placeholder name="OpenFileMenu" />
                <placeholder name="SaveFileMenu">
                <menuitem name="Save" action="DocumentSave" />
                <menuitem name="Revert" action="documenttypes+document+revert" />
                </placeholder>
                <placeholder name="ExtrasFileMenu" />
                <placeholder name="GlobalFileMenu" />
                </menu>
                <menu name="base_edit" action="base_edit_menu">
                <placeholder name="EditMenu">
                    <menuitem name="Undo" action="documenttypes+document+undo" />
                    <menuitem name="Redo" action="documenttypes+document+redo" />
                    <separator />
                    <menuitem name="Cut" action="documenttypes+document+cut" />
                    <menuitem name="Copy" action="documenttypes+document+copy" />
                    <menuitem name="Paste" action="documenttypes+document+paste" />
                </placeholder>
                </menu>
                
                <menu name="base_project" action="base_project_menu">
                </menu>
                <menu name="base_tools" action="base_tools_menu">
                </menu>
                </menubar>
                <toolbar>
                <placeholder name="OpenFileToolbar">
                </placeholder>
                <placeholder name="SaveFileToolbar">
                </placeholder>
                <placeholder name="EditToolbar">
                <toolitem name="Save" action="DocumentSave" />
                <separator />
                <toolitem name="Undo" action="documenttypes+document+undo" />
                <toolitem name="Redo" action="documenttypes+document+redo" />
                <separator />
                <toolitem name="Cut" action="documenttypes+document+cut" />
                <toolitem name="Copy" action="documenttypes+document+copy" />
                <toolitem name="Paste" action="documenttypes+document+paste" />
                </placeholder>
                <placeholder name="ProjectToolbar">
                </placeholder>
                <placeholder name="VcToolbar">
                </placeholder>
            </toolbar>
                """

    def init(self):
        self.__files = {}
        self.__file_fallback = None
        self.__action_groups = {}

    def cmd_register_file_handler(self, handler):
        """Register buffer handler"""
        if handler.globs is None:
            self.__file_fallback = handler(self)
        else:
            self.__register_patterns(self.__files, handler)

    def cmd_create_document(self, filename, document_type=None, **kw):
        handler = (self.__get_file_handler(filename) or
                        self.__file_fallback)
        doc = handler.create_document(filename, document_type, **kw)
        handler.view_document(doc)
        if handler not in self.__action_groups:
            self.boss.call_command('window', 'register_action_group',
                       actiongroup=handler.action_group,
                       uidefinition=handler.get_menu_definition())
            self.__action_groups[handler] = handler.action_group
            handler.action_group.set_visible(False)
        return doc

    def cmd_get_document_actions(self):
        return self.__file_fallback.action_group.list_actions()

    def cmd_disable_document_accelerators(self):
        for act in self.__file_fallback.action_group.list_actions():
            gtk.accel_map_change_entry(act.accel_path, 0, 0, True)

    def __register_patterns(self, handlers, handler, attrname='globs'):
        patterns = getattr(handler, attrname, [])
        for glob_pattern in patterns:
            re_pattern = glob.fnmatch.translate(glob_pattern)
            pattern = sre.compile(re_pattern)
            handlers[pattern] = handler(handler.service)
        
    def __get_file_handler(self, filename):
        if filename is None:
            return False
        for pattern in self.__files:
            if pattern.match(filename):
                return self.__files[pattern]

Service = document_type_handler
