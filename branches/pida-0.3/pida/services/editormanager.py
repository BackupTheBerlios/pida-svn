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

import pida.core.service as service

defs = service.definitions
types = service.types

class editor_manager(service.service):

    class started(defs.event):
        pass

    class general(defs.optiongroup):
        """General editor options"""
        class editor_type(defs.option):
            """Which editor pIDA will use."""
            rtype = types.stringlist(['vim', 'moo'])
            default = 'vimedit'            

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

    def get_editor(self):
        editor = self.opt('general', 'editor_type')
        return self.get_service(editor)
    editor = property(get_editor)

Service = editor_manager

