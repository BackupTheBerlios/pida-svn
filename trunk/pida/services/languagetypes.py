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

# standard library import(s)
import os
import sre
import glob

# gtk import(s)
import gtk

# pida import(s)
import pida.core.actions as actions
import pida.core.service as service
import pida.core.languages as languages

defs = service.definitions

import pida.pidagtk.tree as tree
import pida.pidagtk.contentview as contentview

# TODO: Give the language viewer some love

class language_tree(tree.ToggleTree):
    pass


class language_manager_view(contentview.content_view):
    
    def init(self):
        self.__list = language_tree()
        self.__list.connect('clicked', self.cb_list_activated)
        self.__list.set_property('markup-format-string', '%(display_name)s')
        self.widget.pack_start(self.__list)
        
    def get_key_name_from_class(self, handler):
        key = handler.__class__.__name__
        name = ' '.join(key.capitalize().split('_'))
        return key, name

    def set_file_handlers(self, handlers):
        self.__list.clear()
        for handler in handlers:
            if handler.service.plugin_view is not None:
                key, name = self.get_key_name_from_class(handler)
                handler.display_name = name
                self.__list.add_item(handler, key=key)
        
    def cb_list_activated(self, tv, item):
        item.value.active = not item.value.active
        item.reset_markup()
        handler = item.value
        view = handler.service.plugin_view
        if item.value.active:
            self.service.show_view(view=view)
        else:
            view.detach()
        self.service.call('save_state')


class language_types(service.service):

    class Manager(defs.View):
        view_type = language_manager_view
        book_name = 'ext'

    def init(self):
        self.__langs = {}
        self.__firsts = {}
        self.__action_groups = {}
        self.__current_document = None
        self.__state = os.path.join(self.boss.pida_home, 'data', 'filetypes')
        self.__started = False

    def reset(self):
        if self.__started:
            return
        self.__started = True
        for handler in self.__get_active_handlers():
            if handler.active:
                view = handler.service.plugin_view
                if view is not None:
                    view.set_sensitive(True)
                    self.show_view(view=view)

    def stop(self):
        self.call('save_state')

    def cmd_save_state(self):
        f = open(self.__state, 'w')
        for handler in self.__get_active_handlers():
            f.write('%s\n' % handler.__class__.__name__)
        f.close()

    def cmd_edit(self):
        view = self.create_view('Manager')
        view.set_file_handlers(self.__get_all_handlers())
        self.show_view(view=view)

    def cmd_register_language_handler(self, handler_type):
        handler = handler_type(handler_type.service)
        handler.action_group.set_visible(False)
        self.boss.call_command('window', 'register_action_group',
                               actiongroup=handler.action_group,
                               uidefinition=handler.get_menu_definition())
        self.__register_patterns(self.__langs, handler, 'file_name_globs')
        self.__register_patterns(self.__firsts, handler, 'first_line_globs')
        handler.active = self.__is_active(handler)

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
        self.__disable_all_handlers()
        handlers = self.call('get_language_handlers', document=document)
        for handler in handlers:
            handler.action_group.set_visible(True)
            if handler.service.plugin_view is not None:
                view = handler.service.plugin_view
                if view is not None:
                    view.set_sensitive(True)
            handler.load_document(document)

    def cmd_hide_all_handlers(self):
        self.__disable_all_handlers()

    def __disable_all_handlers(self):
        for handlerlist in self.__langs.values():
            for handler in handlerlist:
                handler.action_group.set_visible(False)
                if hasattr(handler.service, 'lang_view_type'):
                    view = handler.service.lang_view
                    if view is not None:
                        view.set_sensitive(False)

    def __is_active(self, handler):
        if os.path.exists(self.__state):
            actives = []
            f = open(self.__state)
            for line in f:
                actives.append(line.strip())
            f.close()
            return handler.__class__.__name__ in actives
        else:
            return True

    def __get_active_handlers(self):
        for handler in self.__get_all_handlers():
            if handler.active:
                yield handler

    def __get_all_handlers(self):
        handlers = set()
        for globhandlers in self.__langs.values() + self.__firsts.values():
            for handler in globhandlers:
                if handler not in handlers:
                    handlers.add(handler)
                    yield handler

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
                  <menu name="base_tools" action="base_tools_menu">
                  <menu name="service_conf" action="base_service_conf_menu">
                        <menuitem name="editft" action="languagetypes+edit" />
                    </menu>
                    </menu>
                  </menubar>"""
        

Service = language_types
