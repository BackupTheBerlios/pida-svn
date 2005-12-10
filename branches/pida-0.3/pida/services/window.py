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
import pida.pidagtk.window as window
import pida.pidagtk.contentview as contentview
import pida.pidagtk.contentbook as contentbook

import gtk

types = service.types
defs = service.definitions

class PaneSize(types.integer):
    adjustment = 200, 1800, 25    

class window_manager(service.service):
    """Class to control the main window."""


    class layout(defs.optiongroup):
        """The layout options."""
        class sidebar_on_right(defs.option):
            """Whether the sidebar will appear on the right."""
            default = False
            rtype = types.boolean
        class sidebar_width(defs.option):
            """The width of the sidebar."""
            default = 300
            rtype = types.intrange(200, 1800, 25)

    def cmd_update_action_groups(self):
        self.__uim.ensure_update()
        tp = self.toolbar.get_parent()
        if tp:
            tp.remove(self.toolbar)
        self.toolbar = self.__uim.get_widget('/toolbar')
        tp.pack_start(self.toolbar)
        
        #print self.__uim.get_ui()
        ag = self.__uim.get_action_groups()
        for a in ag:
            #print a.get_name(), a.get_visible()
            acts = a.list_actions()
            #for act in acts:
                #print '\t', act, act.get_name(), act.get_visible()

    def cmd_shrink_content(self, bookname):
        self.__window.shrinkbook(bookname)

    def cmd_toggle_content(self, bookname):
        self.__window.toggle_book(bookname)

    def cmd_append_page(self, bookname, view):
        res = self.__window.append_page(bookname, view)
        return res, bookname, view

    def cmd_remove_pages(self, bookname):
        self.__window.remove_pages(bookname)

    def cmd_register_action_group(self, actiongroup, uidefinition):
        self.__uim.insert_action_group(actiongroup, 0)
        self.__uim.add_ui_from_string(uidefinition)
        self.__uim.ensure_update()

    def cmd_unregister_action_group(self, actiongroup):
        self.__uim.remove_action_group(actiongroup)
        actiongroup.set_visible(False)
        self.__uim.ensure_update()

    def init(self):
        self.__window = window.pidawindow(self)
        self.__window.connect('destroy', self.cb_destroy)
        self.__uim = gtk.UIManager()

    def cb_destroy(self, window):
        self.boss.stop()

    def __pack_window(self):
        """Populate the window."""
        #bufferview = self.boss.get_service('buffermanager').view
        #contentbook = self.boss.get_service('contentbook').view
        #viewbook = self.boss.get_service('viewbook').view
        #topbar = self.boss.get_service('topbar').view
        #import gtk


        ##### JUST A SKETCH

        self.buffermanager = self.get_service('buffermanager').single_view
        pluginmanager = contentbook.contentbook()#self.boss.plugins.view
        uim = self.__uim
        for service in self.boss.services:
            if service.plugin_view_type is not None:
                pluginmanager.append_page(service.plugin_view)
            menu_def = service.get_menu_definition()
            if menu_def:
                uim.add_ui_from_string(menu_def)
            ag = service.action_group
            uim.insert_action_group(ag, 0)
        uim.ensure_update()
        self.pluginmanager = pluginmanager
        self.menubar = uim.get_toplevels(gtk.UI_MANAGER_MENUBAR)[0]
        self.toolbar = uim.get_toplevels(gtk.UI_MANAGER_TOOLBAR)[0]
        self.menubar.show_all()
        #editor = self.boss.get_editor().view
        #menu = self.boss.get_service('menubar').view
        #onright = self.options.get('sidebar-on-right').value()
        #vertsb = self.options.get('sidebar-orientation-vertical').value()
        #self.__window.pack(editor, bufferview, pluginmanager, contentbook,
        #    viewbook, topbar, menu, vertsb, onright)
        self.__window.reset()
        

    def reset(self):
        """Display the window."""
        self.__pack_window()
        self.__window.show_all()
        #self.__window.resize_viewbook(-1,
        #                              self.options.get('view-book-height').value())
        #self.__window.resize_contentbook(-1,
        #                              self.options.get('content-book-height').value())
        self.log.debug(self.options)
        #self.__window.resize_sidepane(self.options.get('layout').get('sidebar_width').value)

        pass

    def __get_view(self):
        return self.__window
    view = property(__get_view)

    def cmd_set_title(self, title):
        """Set the window title.
        
        title: a string representation of the new title."""
        self.__window.set_title(title)

    def cmd_shrink_contentbook(self):
        self.view.shrink_contentbook()
        
    def cmd_shrink_viewbook(self):
        self.view.shrink_viewbook()
        
    def cmd_toggle_contentbook(self):
        self.view.toggle_contentbook()
        
    def cmd_toggle_viewbook(self):
        self.view.toggle_viewbook()

Service = window_manager
