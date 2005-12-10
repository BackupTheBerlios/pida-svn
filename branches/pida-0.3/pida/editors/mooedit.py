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

    def init(self, filename=None):
        import gtk
        sw = gtk.ScrolledWindow()
        self.widget.pack_start(sw)
        self.__editor = editor_instance.create_doc(filename)
        sw.add(self.__editor)

class moo_editor(service.service):

    NAME = 'mooedit'

    MULTI_VIEW = moo_view
    MULTI_VIEW_BOOK = 'edit'

    def init(self):
        self.__files = {}
        self.__views = {}

    def cmd_edit(self, filename=None):
        if filename not in self.__files:
            view = self.create_multi_view(filename=filename)
            self.__files[filename] = view
            self.__views[view.unique_id] = filename
        self.__files[filename].raise_page()

    def cmd_start(self):
        self.call('edit_file')

    def cb_multiview_closed(self, view):
        if view.unique_id in self.__views:
            filename = self.__views[view.unique_id]
            self.boss.call_command('buffermanager', 'file_closed',
                                   filename=filename)

Service = moo_editor
