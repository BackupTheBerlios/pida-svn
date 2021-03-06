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
import pida.pidagtk.contentview as contentview

import moo

editor_instance = moo.edit.editor_instance()
editor_instance.get_lang_mgr().add_dir('/usr/local/share/moo-1.0/syntax/')
editor_instance.get_lang_mgr().read_dirs()

class moo_view(contentview.content_view):

    HAS_TITLE = False

    def init(self, filename=None):
        import gtk
        self.widget.set_border_width(6)
        sw = gtk.ScrolledWindow()
        self.widget.pack_start(sw)
        self.__editor = editor_instance.create_doc(filename)
        sw.add(self.__editor)

    def get_editor(self):
        return self.__editor
    editor = property(get_editor)

class moo_config_view(contentview.content_view):

    def init(self):
        prefs = editor_instance.prefs_page()
        prefs.emit('init')
        self.widget.pack_start(prefs)
        self.__prefs = prefs

class moo_editor(service.service):

    NAME = 'mooedit'

    multi_view_type = moo_view
    multi_view_book = 'edit'

    single_view_type = moo_config_view
    single_view_book = 'view'

    def init(self):
        self.__files = {}
        self.__views = {}

    def cmd_edit(self, filename=None):
        if filename not in self.__files:
            self.__load_file(filename)
        self.__view_file(filename)

    def cmd_revert(self):
        #self.__currentview.editor.reload()
        pass

    def __load_file(self, filename):
        view = self.create_multi_view(filename=filename)
        self.__files[filename] = view
        self.__views[view.unique_id] = filename

    def __view_file(self, filename):
        self.__currentview = self.__files[filename]
        self.__files[filename].raise_page()

    def cmd_start(self):
        self.get_service('editormanager').events.emit('started')

    def cmd_goto_line(self, linenumber):
        self.__currentview.editor.move_cursor(linenumber - 1, 0, True)

    def cmd_save(self):
        self.__currentview.editor.save()

    def cmd_undo(self):
        self.__currentview.editor.undo()

    def cmd_redo(self):
        self.__currentview.editor.redo()

    def cmd_cut(self):
        self.__currentview.editor.emit('cut-clipboard')

    def cmd_copy(self):
        self.__currentview.editor.emit('copy-clipboard')

    def cmd_paste(self):
        self.__currentview.editor.emit('paste-clipboard')

    def act_editor_preferences(self, action):
        self.create_single_view()

    def cb_multiview_closed(self, view):
        if view.unique_id in self.__views:
            filename = self.__views[view.unique_id]
            self.boss.call_command('buffermanager', 'file_closed',
                                   filename=filename)

    def get_menu_definition(self):
        return """
        <menubar>
        <menu name="base_tools" action="base_tools_menu">
        <separator />
        <menuitem name="mooconf" action="mooedit+editor_preferences" />
        </menu>
        </menubar>
        """

Service = moo_editor
