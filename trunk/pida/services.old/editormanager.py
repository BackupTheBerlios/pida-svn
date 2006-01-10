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
import contentbook as contentbookservice
import pida.core.registry as registry

def import_editor(name):
    """ Find a named plugin and instantiate it. """
    # import the module
    # The last arg [True] just needs to be non-empty
    try:
        mod = __import__('pida.editors.%s.editor' % name, {}, {}, [True])
        cls = mod.Editor
    except ImportError, e:
        print ('Plugin "%s" failed to import with: %s' % (name, e))
        cls = None
    return cls

class EditorBook(contentbook.ContentBook):

    TABS_VISIBLE = False

    def shrink(self):
        pass

class EditorManager(contentbookservice.Service):
    NAME = 'editor'
    COMMANDS = [['open-file', [('filename', True)]],
                ['open-file-line', [('filename', True), ('linenumber', True)]],
                ['start-editor', []],
                ['save-current', []],
                ['add-page', [('contentview', True)]]]
    EVENTS = ['started', 'file-opened', 'current-file-closed']
    BINDINGS = [('buffermanager', 'file-opened')]
    OPTIONS = [("editor-type", 'The editor used by PIDA', 'vim',
                registry.Editor)]
    VIEW = EditorBook

    editors = ['vim', 'scerpent']

    def init(self):
        for editor_name in self.editors:
            editor_type = import_editor(editor_name)
            if editor_type != None:
                editor_type.boss = self.boss
                editor_type()

    def populate(self):
        editor_name = self.options.get('editor-type').value()
        for editor in self.editors:
            if editor != editor_name:
                self.boss.hide_option_group(editor)
        editor_type = import_editor(editor_name)
        editor_type.boss = self.boss
        editor_type.manager = self
        self.__editor = editor_type()
        contentbookservice.Service.populate(self)
        self.__editor.populate()

    def cmd_add_page(self, contentview):
        self.view.append_page(contentview)

    def cmd_start_editor(self):
        self.__editor.launch()

    def cmd_open_file(self, filename):
        self.__editor.open_file(filename)

    def cmd_open_file_line(self, filename, linenumber):
        self.__editor.open_file_line(filename, linenumber)

    def cmd_save_current(self):
        self.__editor.save_current()

    def stop(self):
        pass

    def reset(self):
        self.__editor.reset()

    #def evt_buffermanager_file_opened(self, buffer):
    #    self.cmd_open_file(buffer.filename)

Service = EditorManager
