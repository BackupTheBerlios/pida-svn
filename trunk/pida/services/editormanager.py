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

from pida.core import service
from pida.core.errors import *

defs = service.definitions
types = service.types

class editor_manager(service.service):

    display_name = 'Editor'

    def init(self):
        self.__editor = None
        self.__editorname = None

    class started(defs.event):
        pass

    class general(defs.optiongroup):
        """General editor options"""
        class editor_type(defs.option):
            """Which editor pIDA will use."""
            rtype = types.stringlist('Vim', 'Vim external', 'Culebra')
            default = 'Vim'            

    def reset(self):
        if self.__editorname is not None and self.get_editor_name() != self.__editorname:
            self._editor_changed_message()

    def _editor_changed_message(self):
        msg = ('The editor type has changed. You must restart PIDA for the'
               'new editor to be started.')
        dlg = gtk.MessageDialog(parent=self.boss.get_main_window(),
                                flags=0,
                                type=gtk.MESSAGE_WARNING,
                                buttons=gtk.BUTTONS_OK,
                                message_format=msg)
        def _response(dlg, response):
            dlg.destroy()
        dlg.connect('response', _response)
        dlg.show_all()

    def cmd_close(self, filename):
        self.editor.call('close', filename=filename)

    def cmd_revert(self):
        self.editor.call('revert')
    
    def cmd_start(self):
        self.editor.call('start')

    def cmd_edit(self, filename):
        self.editor.call('edit', filename=filename)

    def cmd_goto_line(self, linenumber):
        self.editor.call('goto_line', linenumber=linenumber)

    def cmd_save(self):
        self.editor.call('save')

    def cmd_undo(self):
        self.editor.call('undo')

    def cmd_redo(self):
        self.editor.call('redo')

    def cmd_cut(self):
        self.editor.call('cut')

    def cmd_copy(self):
        self.editor.call('copy')

    def cmd_paste(self):
        self.editor.call('paste')

    def cmd_can_close(self):
        # XXX: this should go away when all the editors implement it
        # XXX: see ticket #102
        try:
            return self.editor.call('can_close')
        except CommandNotFoundError:
            return True

    def get_editor_name(self):
        # XXX: there should be a key, value tupple, so this
        # XXX: checking could be made unexistant. see ticket #101
        editor_name = self.opt('general', 'editor_type')
        if editor_name == 'Vim':
            editor = 'vimedit'
        elif editor_name == 'Moo':
            editor = 'mooedit'
        elif editor_name == 'Vim external':
            editor = 'vimmultiedit'
        elif editor_name == 'Culebra':
            editor = 'culebraedit'
        else:
            self.log.error('No text editor')
            editor = 'No working editor'
        return editor
    editor_name = property(get_editor_name)

    def get_editor(self):
        if self.__editor is None:
            self.__editorname = self.get_editor_name()
            self.__editor = self.get_service(self.__editorname)
        return self.__editor
    editor = property(get_editor)

Service = editor_manager

