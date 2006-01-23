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

import gtk

from pida.pidagtk import contentview
from pida.core import actions
from pida.core import service
from pida.utils.culebra import edit

from rat import hig


class culebra_view(contentview.content_view):

    HAS_TITLE = False

    def init(self, filename=None, action_group=None):
        self.widget.set_no_show_all(True)
        widget, editor = edit.create_widget(filename, action_group)
        self.__editor = editor
        widget.show()
        self.widget.add(widget)

    def get_editor(self):
        return self.__editor
        
    editor = property(get_editor)

    def get_buffer(self):
        return self.__editor.get_buffer()
        
    buffer = property(get_buffer)

class culebra_editor(service.service):

    display_name = 'Culebra Text Editor'

    multi_view_type = culebra_view
    multi_view_book = 'edit'
    
    def init(self):
        
        self.__files = {}
        self.__views = {}

    def cmd_edit(self, filename=None):
        if filename not in self.__files:
            self.__load_file(filename)
        self.__view_file(filename)

    def cmd_revert(self):
        raise NotImplementedError

    def __load_file(self, filename):
        view = self.create_multi_view(
            filename=filename,
            action_group=self.action_group
        )
        self.__files[filename] = view
        self.__views[view.unique_id] = filename

    def __view_file(self, filename):
        self.current_view = self.__files[filename]
        self.__files[filename].raise_page()

    #############
    # Callbacks
    def cmd_start(self):
        self.get_service('editormanager').events.emit('started')

    def cmd_goto_line(self, linenumber):
        view = self.current_view.editor
        buff = self.current_view.buffer
        
        # Get line iterator
        line_iter = buff.get_iter_at_line(linenumber - 1)
        # Move scroll to the line iterator
        view.scroll_to_iter(line_iter, 0.25)
        # Place the cursor at the begining of the line
        buff.place_cursor(line_iter)
        
    def cmd_save(self):
        self.current_view.buffer.save()
        self.boss.call_command('buffermanager', 'reset_current_document')

    def cmd_undo(self):
        self.current_view.editor.emit('undo')

    def cmd_redo(self):
        self.current_view.editor.emit('redo')

    def cmd_cut(self):
        self.current_view.editor.emit('cut-clipboard')

    def cmd_copy(self):
        self.current_view.editor.emit('copy-clipboard')

    def cmd_paste(self):
        self.current_view.editor.emit('paste-clipboard')

    def cmd_can_close(self):
        buffs = [view.buffer for view in self.__files.values() if view.buffer.get_modified()]
        # If we have no buffers to save, go on
        if len(buffs) == 0:
            return True
            
        filenames = dict(map(lambda buff: (buff.filename, buff), buffs))
        parent = self.boss.get_main_window()
        files, response = hig.save_changes(filenames.keys(), parent=parent)
        # Save the files that need to be saved
        for filename in files:
            # XXX: handle new files
            filenames[filename].save()
        return response in (gtk.RESPONSE_CLOSE, gtk.RESPONSE_OK)
        
    def cb_multi_view_closed(self, view):
        if view.unique_id in self.__views:
            filename = self.__views[view.unique_id]
            del self.__views[view.unique_id]
            del self.__files[filename]
            self.boss.call_command('buffermanager', 'file_closed',
                                   filename=filename)

    def confirm_multi_view_controlbar_clicked_close(self, view):
        buff = view.buffer
        
        # If buffer was not modified you can safely close it
        if not buff.get_modified():
            return True
        
        # When the buffer is new then we need to show the save dialog instead
        # of a save changes dialog:
        if buff.is_new:
            # XXX: this is utterly broken but there's no support for new files
            # either
            return False
        
        parent = self.boss.get_main_window()
        files, response = hig.save_changes(
            [buff.filename],
            parent=parent
        )
        
        if response == gtk.RESPONSE_OK:
            buff.save()
            
        return response in (gtk.RESPONSE_OK, gtk.RESPONSE_CLOSE)

            
    ############################
    # UIManager definition
    
    def get_menu_definition(self):
        return """
        <toolbar>
            <placeholder name="ProjectToolbar">
                <toolitem name="CulebraFindToggle"
                action="%s" />
                <toolitem name="CulebraReplaceToggle"
                action="%s" />
            </placeholder>
        </toolbar>
        """ % (edit.ACTION_FIND_TOGGLE, edit.ACTION_REPLACE_TOGGLE)
    
    ####################################
    # gtk.Action's definition
    @actions.action(
        name = edit.ACTION_FIND_TOGGLE,
        stock_id = gtk.STOCK_FIND,
        label = "_Find...",
        type = actions.TYPE_TOGGLE,
    )
    def act_find_toggle(self, action):
        """Search for text"""
    
    @actions.action(
        name = edit.ACTION_REPLACE_TOGGLE,
        stock_id = gtk.STOCK_FIND_AND_REPLACE,
        label = "_Replace...",
        type = actions.TYPE_TOGGLE,
    )
    def act_replace_toggle(self, action):
        """Search and replace text"""
    
    @actions.action(
        name = edit.ACTION_FIND_FORWARD,
        stock_id = gtk.STOCK_GO_FORWARD,
    )
    def act_find_forward(self, action):
        """Find next matching word"""
    
    @actions.action(
        name = edit.ACTION_FIND_BACKWARD,
        stock_id = gtk.STOCK_GO_BACK,
    )
    def act_find_backward(self, action):
        """Find previous mathing word"""

    @actions.action(
        name = edit.ACTION_REPLACE_FORWARD,
        stock_id = gtk.STOCK_GO_FORWARD,
    )
    def act_replace_forward(self, action):
        """Replaces the next matching word"""

    @actions.action(
        name = edit.ACTION_REPLACE_BACKWARD,
        stock_id = gtk.STOCK_GO_BACK,
    )
    def act_replace_backward(self, action):
        """Replaces backward"""
    
    @actions.action(
        name = edit.ACTION_REPLACE_ALL,
        stock_id = gtk.STOCK_FIND_AND_REPLACE,
        label = "Replace Alll"
    )
    def act_replace_all(self, action):
        """Replaces all matching words"""
        


Service = culebra_editor
