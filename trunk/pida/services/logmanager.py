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

import time
import gtk

#import pida.pidagtk.logmanager as logmanager
import pida.pidagtk.tree as tree
import pida.pidagtk.toolbar as toolbar
import pida.pidagtk.contentview as contentview

# pida utils import
import pida.core.service as service

from logging import Formatter
from logging import getLevelName

class LogItem(tree.TreeItem):
    def __init__(self,record):
        tree.TreeItem.__init__(self, record.created, record)

    def __get_created(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.value.created))
    created = property(__get_created)

    def __get_message(self):
        return self.value.getMessage()
    message = property(__get_message)

class LogTree(tree.Tree):
    '''Tree listing all the pastes'''
    EDIT_BUTTONS = False
    SORT_BY = 'created'

    markup_format_string =  ('%(created)s %(message)s')

    def __init__(self):
        '''Initializes the tree'''
        tree.Tree.__init__(self)
        self.set_property('markup-format-string', self.markup_format_string)

    def push(self, record):
        '''Adds a paste to the Tree'''
        self.add_item(LogItem(record))

    def pop(self):
        '''Deletes the currently selected paste'''
        self.del_item()

class LogManager(contentview.content_view):
#    ICON_NAME = ''
    LONG_TITLE = 'Log viewer/filter'
    SHORT_TITLE = 'log'
    ICON_TEXT = 'files'
    HAS_CONTROL_BOX = True
    HAS_DETACH_BUTTON = True
    HAS_CLOSE_BUTTON = True
    HAS_SEPARATOR = False
    HAS_TITLE = True

    def init(self,filter='',logs=None):
        '''Constructor of the Paste History View.'''

        print 'new log manager : FILTER=%s' % filter

        self.__logs = logs
        
        hb = gtk.HBox()
        hb.add(gtk.Label('Filter'))
        self.__filter_entry = gtk.Entry()
        hb.add(self.__filter_entry)
        self.__filter_add = gtk.Button('Add','Add')
        self.__filter_add.set_use_stock(True)
        self.__filter_add.connect('clicked', self.cb_filter_add)
        hb.add(self.__filter_add)
        self.widget.pack_start(hb,False,False)

        self.__history_tree = LogTree()
        self.widget.pack_start(self.__history_tree)
#        self.__x11_clipboard = gtk.Clipboard(selection="PRIMARY")
#        self.__gnome_clipboard = gtk.Clipboard(selection="CLIPBOARD")
#        self.__registry = registry.registry()
        self.__tree_selected = None
        self.__history_tree.connect('clicked', self.cb_paste_clicked)
        self.__history_tree.connect('double-clicked', self.cb_paste_db_clicked)
        self.__history_tree.connect('middle-clicked', self.cb_paste_m_clicked)
        self.__history_tree.connect('right-clicked', self.cb_paste_r_clicked)
#        self.__uim = gtk.UIManager()
#        self.__uim.insert_action_group(self.service.action_group, 0)
#        self.__uim.add_ui_from_string("""
#            <popup>
#            <menuitem name="1" action="pastemanager+new_paste" />
#            <separator />
#            <menuitem name="2" action="pastemanager+view_paste" />
#            <menuitem name="3" action="pastemanager+copy_url_to_clipboard" />
#            <separator />
#            <menuitem name="5" action="pastemanager+remove_paste" />
#            </popup>
#            """)
#        self.__popup_menu = self.__uim.get_widget('/popup')

    # Public interface

    def refresh(self):
        self.__history_tree.clear()
        for log in self.__logs.dict.values(): # Here apply the filter
            self.__history_tree.push(log)

    # Actions

    def cb_filter_add(self,but):
#        self.service.create_multi_view(filter=self.__filter_entry.get_text())
        self.service.boss.log.warn("It's only a test...")

    def cb_paste_clicked(self,paste,tree_item):
        '''Callback function called when an item is selected in the TreeView'''
        self.__tree_selected = tree_item.value

    def cb_paste_db_clicked(self,paste,tree_item):
        '''Callback function called when an item is double clicked, and copy it
        to the gnome/gtk clipboard'''
        if self.__tree_selected != None:
            pass
            # self.__gnome_clipboard.set_text(self.__tree_selected.get_url())
            # aa: view the paste
#            self.service.call('view_paste', paste=self.__tree_selected)

    def cb_paste_m_clicked(self,paste,tree_item):
        '''Callback function called when an item is middle clicked, and copy it
        to the mouse buffer clipboard'''
        if self.__tree_selected != None:
#            self.__x11_clipboard.set_text(self.__tree_selected.get_url())
            pass

    def cb_paste_r_clicked(self, paste, tree_item, event):
#        sensitives = (tree_item is not None)
#        for action in ['pastemanager+remove_paste',
#                       'pastemanager+view_paste',
#                       'pastemanager+copy_url_to_clipboard']:
#            self.service.action_group.get_action(action).set_sensitive(sensitives)
#        self.__popup_menu.popup(None, None, None, event.button, event.time)
        pass

class log_manager(service.service):
    NAME = 'log manager'
    LONG_TITLE = 'log manager'

    multi_view_type = LogManager
    multi_view_book = 'content'

    # life cycle

    def start(self):
        self.__view = None
        self.__first = True
        print "UI started"
        if self.boss.set_view_handler():
            self.boss.log.info("Logging service started.")
        else: 
            self.stop()

    def reset(self):
        self.boss.log.info("Logging service reset.")

    def stop(self):
        self.boss.log.info("Logging service stopped.")
        #Do more..

    #private interface
    #public interface
    # commands

    def cmd_filter(self,filter):
        self.create_multi_view(filter=filter,logs=self.boss.logs)
        print "LAUNCH NEW FILTER !!!"

    def cmd_get(self,):
        print 'LOGMANAGER: %s' % record.getMessage()

    def cmd_refresh(self):
        for view in self.multi_views:
            view.refresh()
        else:
            if self.__first:
                self.__first = False
                self.create_multi_view(logs=self.boss.logs)

    # ui actions

#    def act_new_paste(self, action):
#        self.call('create_paste')
#
#    def act_remove_paste(self, action):
#        self.plugin_view.remove_current_paste()
#
#    def act_copy_url_to_clipboard(self, action):
#        self.plugin_view.copy_current_paste()
#
#    def act_view_paste(self, action):
#        self.plugin_view.view_current_paste()
#
#    def get_menu_definition(self):
#        return """<menubar>
#                  <menu name="base_tools" action="base_tools_menu">
#                  <separator />
#                  <menuitem name="newpaste" action="pastemanager+new_paste" />
#                  <separator />
#                  </menu>
#                  </menubar>
#               """


Service = log_manager
