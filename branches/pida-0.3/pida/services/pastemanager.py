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

import pida.pidagtk.tree as tree
import pida.pidagtk.configview as configview
import pida.pidagtk.contentbook as contentbook
import pida.pidagtk.contentview as contentview
import pida.pidagtk.contextwidgets as contextwidgets

import pida.utils.pastebin as pastebin

import pida.core.registry as registry
import pida.core.service as service
types = service.types
defs = service.definitions

import gtk
import os
import gobject
import os.path

class paste_manager(service.service):
    """Service that manages the pastes and the pastebins"""

    # life cycle
    def start(self):
        '''Initialization'''
        self.__pastes = []

    def reset(self):
        '''Reset'''
        self.__pastes = []

    def stop(self):
        pass

    # private interface

    def __add_paste(self, paste):
        '''Adds a paste to the list'''
        self.__pastes.append(paste)

    def __send_paste(self, paste):
        '''Trigger the paste's posting'''
        paste.paste()

    def __del_paste(self, paste):
        '''Remove paste 'paste' from the list'''
        self.__pastes.remove(paste)

    def __get_paste(self, paste_id):
        '''Returns a paste depending on paste_id (deprecated)'''
        for paste in self.__pastes:
            if (paste.get_id == paste_id):
                return paste

    def __refresh(self):
        '''Refresh the history list'''
        self.boss.call_command('pastehistory','refresh',pastes=self.pastes)

    # external interface

    def get_pastes(self):
        '''Returns an iterator on the paste list'''
        for paste in self.__pastes:
            yield paste
    pastes = property(get_pastes)

    def push(self, paste):
        '''Add a paste to the pastelist and refresh'''
        self.__add_paste(paste)
        self.__refresh()

    # commands

    def cmd_create_paste(self, paste):
        '''Command to create a new paste
        
           Opens a new editor
        '''
        pbin = pastebin.BINS[paste]()
        self.boss.call_command('pasteeditor','create_paste',paste=pbin)

    def cmd_post_paste(self, paste):
        '''Post the paste paste'''
        paste.set_mgr(self)
        paste.paste()

    def cmd_post_annotation(self, annotation):
        '''TODO: Annotates a post'''
        print "TODO: Post annotation"

    def cmd_view_paste(self, paste):
        '''View a paste'''
        self.boss.call_command('pasteeditor','view_paste',paste=paste)

    def cmd_annotate_paste(self, paste):
        '''Create a new annotation'''
        self.boss.call_command('pasteeditor','annotate_paste',paste=paste)

    def cmd_delete_paste(self, paste):
        '''Delete a paste'''
        self.__del_paste(paste)
        self.__refresh()

    def cmd_get_pastes(self):
        '''Get all pastes'''
        return pastes

    # UI Definitions

    def act_new_paste(self, action):
        paste = self.boss.call_command('paste_history','get_selected')
        self.boss.call_command('paste_editor','post_paste',paste)

    def get_menu_definition(self):
        return """
                <menubar>
                <menu name="base_edit" action="base_edit_menu">
                <menuitem name="newpaste" action="paste-manager+new_paste" />
                </menu>
                </menubar>
        """

Service = paste_manager
