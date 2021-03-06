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

import gtk

import pida.core.service as service
import pida.pidagtk.contentview as contentview

from pida.utils.culebra import edit


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
        self._create_actions()

    def cmd_edit(self, filename=None):
        if filename not in self.__files:
            self.__load_file(filename)
        self.__view_file(filename)

    def cmd_revert(self):
        raise NotImplementedError

    def __load_file(self, filename):
        view = self.create_multi_view(
            filename=filename,
            action_group=self._action_group
        )
        self.__files[filename] = view
        self.__views[view.unique_id] = filename

    def __view_file(self, filename):
        self.current_view = self.__files[filename]
        self.__files[filename].raise_page()

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

    def cb_multiview_closed(self, view):
        if view.unique_id in self.__views:
            filename = self.__views[view.unique_id]
            self.boss.call_command('buffermanager', 'file_closed',
                                   filename=filename)

    def _create_actions(self):
        ui_def = """
        <toolbar>
            <placeholder name="OpenFileToolbar" />
            <placeholder name="SaveFileToolbar" />
            
            <placeholder name="EditToolbar">
                <toolitem name="culebra_find_toggle"
                action="%s" />
                <toolitem name="CulebraReplaceToggle"
                action="%s" />
            </placeholder>
            
            <placeholder name="ProjectToolbar" />
            <placeholder name="VcToolbar" />
            <placeholder name="ToolsToolbar"/>
        </toolbar>
        """ % (edit.ACTION_FIND_TOGGLE, edit.ACTION_REPLACE_TOGGLE)
        

        ag = gtk.ActionGroup("culebraactions")
        ag.add_toggle_actions((
            (
                edit.ACTION_FIND_TOGGLE,
                gtk.STOCK_FIND,
                "_Find...",
                None,
                "Shows or hides the find bar"
            ),
            
            (
                edit.ACTION_REPLACE_TOGGLE,
                gtk.STOCK_FIND_AND_REPLACE,
                "_Replace...",
                None,
                "Shows or hides the replace bar"
            ),
            
        ))
        
        ag.add_actions((
            (
                edit.ACTION_FIND_FORWARD,
                gtk.STOCK_GO_FORWARD,
                "Find Forward",
                None,
                "Finds the next matching word"
            ),
            (
                edit.ACTION_FIND_BACKWARD,
                gtk.STOCK_GO_BACK,
                "Find Backward",
                None,
                "Finds the previous matching word"
            ),
            (
                edit.ACTION_REPLACE_FORWARD,
                gtk.STOCK_GO_FORWARD,
                "Replace Forward",
                None,
                "Replaces the next matching word"
            ),
            (
                edit.ACTION_REPLACE_BACKWARD,
                gtk.STOCK_GO_BACK,
                "Replace Backward",
                None,
                "Replaces the previous matching word"
            ),
            (
                edit.ACTION_REPLACE_ALL,
                gtk.STOCK_FIND_AND_REPLACE,
                "Replace All",
                None,
                "Replaces every the matching word"
            ),
            
        ))
        
        self._action_group = ag
        self.boss.call_command(
            "window",
            "register_action_group",
            actiongroup=ag,
            uidefinition=ui_def
        )
        

Service = culebra_editor
