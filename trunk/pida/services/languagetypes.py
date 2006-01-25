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
import glob
import sre
import pida.core.service as service
import pida.core.languages as languages
import pida.core.actions as actions
import pida.pidagtk.contentview as contentview
import gtk
import pida.pidagtk.tree as tree

class language_tree(tree.ToggleTree):
    pass

class language_manager_view(contentview.content_view):
    
    def init(self):
        self.__list = language_tree()
        self.__list.connect('double-clicked', self.cb_list_activated)
        self.widget.pack_start(self.__list)
        
    def set_file_handlers(self, handlers):
        self.__list.clear()
        for handler in handlers:
            self.__list.add_item(handler, key=handler.__class__.__name__)
        
    def cb_list_activated(self, tv, item):
        item.value.active = not item.value.active
        item.reset_markup()
        self.service.call('show_handlers')

    



class language_types(service.service):

    single_view_type = language_manager_view
    single_view_book = 'ext'

    def init(self):
        self.__langs = {}
        self.__firsts = {}
        self.__action_groups = {}
        self.__current_document = None

    def cmd_edit(self):
        self.create_single_view()
        handlers = set()
        for globhandlers in self.__langs.values() + self.__firsts.values():
            for handler in globhandlers:
                handlers.add(handler)
        self.single_view.set_file_handlers(handlers)

    def cmd_register_language_handler(self, handler_type):
        handler = handler_type(handler_type.service)
        handler.action_group.set_visible(False)
        self.boss.call_command('window', 'register_action_group',
                               actiongroup=handler.action_group,
                               uidefinition=handler.get_menu_definition())
        self.__register_patterns(self.__langs, handler, 'file_name_globs')
        self.__register_patterns(self.__firsts, handler, 'first_line_globs')

    def cmd_get_language_handlers(self, document):
        # will break on meld
        handlers = ([h for h in self.__get_lang_handler(document.filename) +
                                self.__get_first_handler(document.lines[:3])
                            if h.active])
        return set(handlers)

    def cmd_show_handlers(self, document=None):
        if document is None:
            document = self.__current_document
        else:
            self.__current_document = document
        if document is None:
            return
        for handlerlist in self.__langs.values():
            for handler in handlerlist:
                handler.action_group.set_visible(False)
                if hasattr(handler.service, 'lang_view_type'):
                    view = handler.service.lang_view
                    view.set_sensitive(False)
        self.boss.call_command('window', 'remove_pages', bookname='languages')
        handlers = self.call('get_language_handlers', document=document)
        for handler in handlers:
            handler.action_group.set_visible(True)
            if hasattr(handler.service, 'lang_view_type'):
                view = handler.service.lang_view
                view.set_sensitive(True)
                self.boss.call_command('window', 'append_page',
                                       bookname='languages',
                                       view=view)
            handler.load_document(document)

    def __register_patterns(self, handlers, handler, attrname='globs'):
        patterns = getattr(handler, attrname, [])
        for glob_pattern in patterns:
            re_pattern = glob.fnmatch.translate(glob_pattern)
            pattern = sre.compile(re_pattern)
            handlers.setdefault(pattern, []).append(handler)
        
    def __get_lang_handler(self, filename):
        matches = []
        for pattern in self.__langs:
            if pattern.match(filename):
                matches = matches + self.__langs[pattern]
        return matches

    def __get_first_handler(self, lines):
        matches = []
        for line in lines:
            for pattern in self.__firsts:
                if pattern.match(line):
                    matches = matches + self.__firsts[pattern]
        return matches


    @actions.action(
        stock_id = 'configure',
        label = 'File Type Plugins',
    )
    def act_edit(self, action):
        """File Types Plugins"""
        self.call('edit')

    def get_menu_definition(self):
        return """<menubar>
                    <menu name="base_tools">
                        <menuitem name="editft" action="languagetypes+edit" />
                    </menu>
                </menubar>"""
        
            

Service = language_types
