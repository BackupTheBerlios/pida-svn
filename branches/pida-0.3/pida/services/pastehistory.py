# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com
#Copyright (c) 2006 Bernard Pratz aka Guyzmo, guyzmo@m0g.net

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

import pida.pidagtk.tree as tree
import pida.pidagtk.configview as configview
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.contentview as contentview
import pida.pidagtk.contextwidgets as contextwidgets

import pida.pidagtk.gladeview as gladeview

import pida.utils.pastebin as pastebin

import pida.core.registry as registry
import pida.core.service as service
types = service.types
defs = service.definitions

import gtk
import os
import gobject
import os.path

class paste_tree(tree.Tree):
    '''Tree listing all the pastes'''
    EDIT_BUTTONS = False
    SORT_BY = 'date'

    markup_format_string = ('<span size="small"><b>%(title)s</b> ('
            '<span foreground="#0000c0">%(syntax)s</span>)\n'
            '%(url)s</span>')
        
    def __init__(self):
        '''Initializes the tree'''
        tree.Tree.__init__(self)
        self.set_property('markup-format-string', self.markup_format_string)
                
    def push_paste(self, paste):
        '''Adds a paste to the Tree'''
        self.add_item(paste, key=paste.date)

    def del_paste(self):
        '''Deletes the currently selected paste'''
        self.del_item()

class paste_history_view(gladeview.glade_view):
    SHORT_TITLE = 'Paste History'
    LONG_TITLE = 'Paste History'
    ICON_NAME = 'paste'
    HAS_CONTROL_BOX = False
    HAS_DETACH_BUTTON = True
    HAS_CLOSE_BUTTON = False
    HAS_SEPARATOR = False
    HAS_TITLE = True

    glade_file_name = 'paste-history.glade'

    def init(self):
        gladeview.glade_view.init(self)

    def create_paste_tree(self, str1, str2, int1, int2):
        '''Returns a paste_tree object'''
        return paste_tree()

    def create_list_box(self, str1, str2, int1, int2):
        '''Returns a ComboBox object'''
        return gtk.combo_box_new_text()

    def init_glade(self):
        '''Constructor of the Paste History View.'''
        self.__history_tree = self.get_widget('paste_tree')
        self.__list_sites = self.get_widget('list_sites')

        self.__x11_clipboard = gtk.Clipboard(selection="PRIMARY")
        self.__gnome_clipboard = gtk.Clipboard(selection="CLIPBOARD")
        self.__registry = registry.registry()

        for site in pastebin.BINS.keys():
            self.__list_sites.append_text(site)
            
        self.__list_sites.set_active(0)
        self.__list_selected = self.__list_sites.get_active_text()

        self.__tree_selected = None

        self.__history_tree.connect('clicked', self.cb_paste_clicked)
        self.__history_tree.connect('double-clicked', self.cb_paste_db_clicked)
        self.__history_tree.connect('middle-clicked', self.cb_paste_m_clicked)
        self.__list_sites.connect('changed', self.cb_list_site_change)

    def set(self, pastes):
        '''Sets the paste list to the tree view.
           First reset it, then rebuild it.
        '''
        self.__history_tree.clear()
        for paste in pastes:
            self.__history_tree.push_paste(paste)
        self.__tree_selected = None

    def on_add__clicked(self, but):
        '''Callback function bound to the toolbar button new that creates a new
        paste to post'''
        if self.__list_selected != None:
            self.service.boss.call_command('pastemanager','create_paste',
                paste=self.__list_selected)
        else:
            print "ERROR: No paste bin selected"

    def on_copy__clicked(self,but):
        '''Callback function bound to the toolbar button view that copies the
        selected paste'''
        self.__x11_clipboard.set_text(self.__tree_selected.get_url())
        self.__gnome_clipboard.set_text(self.__tree_selected.get_url())

    def on_view__clicked(self,but):
        '''Callback function bound to the toolbar button view that shows the
        selected paste'''
        if self.__tree_selected != None:
            self.service.boss.call_command('pastemanager','view_paste',
                paste=self.__tree_selected)
        else:
            print "ERROR: No paste selected"

    def on_annotate__clicked(self,but):
        '''Callback function bound to the toolbar button view that annotates
        selected paste'''
        if self.__tree_selected != None:
            self.service.boss.call_command('pastemanager','annotate_paste',
                paste=self.__tree_selected)
        else:
            print "ERROR: No paste selected"

    def on_remove__clicked(self,but):
        '''Callback function bound to the toolbar button delete that removes the
        selected paste'''
        if self.__tree_selected != None:
            self.service.boss.call_command('pastemanager','delete_paste',
                paste=self.__tree_selected)
        else:
            print "ERROR: No paste selected"

    def cb_list_site_change(self, list):
        '''Callback function called on pastebin sites list change'''
        self.__list_selected = self.__list_sites.get_active_text()

    def cb_paste_clicked(self,paste,tree_item):
        '''Callback function called when an item is selected in the TreeView'''
        self.__tree_selected = tree_item.value

    def cb_paste_db_clicked(self,paste,tree_item):
        '''Callback function called when an item is double clicked, and copy it
        to the gnome/gtk clipboard'''
        self.__gnome_clipboard.set_text(self.__tree_selected.get_url())

    def cb_paste_m_clicked(self,paste,tree_item):
        '''Callback function called when an item is middle clicked, and copy it
        to the mouse buffer clipboard'''
        self.__x11_clipboard.set_text(self.__tree_selected.get_url())

class paste_history(service.service):
    """Displays paste history"""

    # view definitions

    plugin_view_type = paste_history_view

    single_view_type = configview.config_view
    single_view_book = 'ext'

    def init(self):
        pass

    def reset(self):
        pass

    def stop(self):
        pass

    # commands

    def cmd_refresh(self, pastes):
        self.plugin_view.set(pastes)
            


Service = paste_history
