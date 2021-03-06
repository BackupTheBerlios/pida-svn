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

from rat import hig
from gtk import gdk

from pida.pidagtk import contentview
from pida.core import actions
from pida.core import service
from pida.utils.culebra import edit, sensitive, common


defs = service.definitions
types = service.types

#temporary
C = gtk.gdk.CONTROL_MASK
SC = gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK

KEYMAP = {
    'DocumentSave': (115, C),
    'documenttypes+document+undo': (122, C),
    'documenttypes+document+redo': (122, SC),
    'documenttypes+document+cut': (120, C),
    'documenttypes+document+copy': (99, C),
    'documenttypes+document+paste': (118, C),
}

class culebra_view(contentview.content_view):

    HAS_TITLE = False

    def init(self, filename=None, action_group=None, background_color=None, font_color=None):
        self.widget.set_no_show_all(True)
        widget, editor = edit.create_widget(filename, action_group)
        editor.set_background_color(background_color)
        editor.set_font_color(font_color)
        self.__editor = editor
        widget.show()
        self.widget.add(widget)

    def get_editor(self):
        return self.__editor
        
    editor = property(get_editor)

    def get_buffer(self):
        return self.__editor.get_buffer()
        
    buffer = property(get_buffer)

    def connect_keys(self):
        self.__editor.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.__editor.connect('key-press-event', self.cb_keypress)

    def cb_keypress(self, widg, event):
        key, mod = event.keyval, event.state
        return self.service.received_key(key, mod)
        

class culebra_editor(service.service):

    display_name = 'Culebra Text Editor'

    multi_view_type = culebra_view
    multi_view_book = 'edit'
    
    class general(defs.optiongroup):
        class background_color(defs.option):
            """Change the background color"""
            default = "#FFFFFF"
            rtype = types.color
        
        class font_color(defs.option):
            """Change the font color"""
            default = "#000000"
            rtype = types.color
            
    ############
    # Service related methods
    def init(self):
        
        self.__files = {}
        self.__views = {}
        self.__keymods = {}

    def reset(self):
        actions = self.boss.call_command("documenttypes", "get_document_actions")
        for action in actions:
            actname = action.get_name()
            if actname in KEYMAP:
                self.__keymods[KEYMAP[actname]] = action
        for view in self.__files.values():
            view.editor.set_background_color(self.get_background_color())
            view.editor.set_font_color(self.get_font_color())
    
    #############
    # Methods
    def get_background_color(self):
        color = self.opt("general", "background_color")
        return gdk.color_parse(color)
    
    def get_font_color(self):
        color = self.opt("general", "font_color")
        return gdk.color_parse(color)
        
    def __load_file(self, filename):
        view = self.create_multi_view(
            filename=filename,
            action_group=self.action_group,
            background_color = self.get_background_color(),
            font_color = self.get_font_color(),
        )
        self.__files[filename] = view
        self.__views[view.unique_id] = filename
        view.connect_keys()

    def __view_file(self, filename):
        self.current_view = self.__files[filename]
        self.__files[filename].raise_page()
    
    ####################
    # get_action
    _save_action = None

    def _create_save_action(self):
        actions = self.boss.call_command("documenttypes", "get_document_actions")
        for action in actions:
            if action.get_name() == "DocumentSave":
                return action
        assert False, "Document Save action not found"
    
    def get_save_action(self):
        if self._save_action is None:
            self._save_action = self._create_save_action()
        return self._save_action

    # keyboard bindings
    
    def received_key(self, key, mod):
        if (key, mod) in self.__keymods:
            self.__keymods[key, mod].emit('activate')
            return True
        else:
            return False
    
    def get_window(self):
        return self.boss.get_main_window()

    #############
    # Commands
    current_view = None
    def cmd_edit(self, filename=None):
        if self.current_view is not None:
            self.current_view.editor.set_action_group(None)
            
        if filename not in self.__files:
            self.__load_file(filename)
        self.__view_file(filename)
        save_action = self.get_save_action()
        assert save_action is not None
        buff = self.current_view.editor.get_buffer()
        self.current_view.editor.set_action_group(self.action_group)
        self.linker = sensitive.SaveLinker(buff, save_action)
            
            
    def cmd_revert(self):
        if self.current_view is None:
            return
            
        buff = self.current_view.editor.get_buffer()
        if buff.is_new:
            return
        
        # Ok the buffer is not new and exists
        reply = hig.dialog_ok_cancel(
            "Revert the document to saved contents",
            ("Even if your document was just saved it could be altered by a "
             "third party. By reverting to its real contents you will loose "
             "all the changes you've made so far."),
            parent = self.get_window(),
            ok_button = gtk.STOCK_REVERT_TO_SAVED,
        )
        if reply == gtk.RESPONSE_OK:
            buff.load_from_file()
            self.boss.call_command('buffermanager', 'reset_current_document')

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
        parent = self.get_window()
        files, response = hig.save_changes(filenames.keys(), parent=parent)
        # Save the files that need to be saved
        for filename in files:
            # XXX: handle new files
            filenames[filename].save()
        return response in (gtk.RESPONSE_CLOSE, gtk.RESPONSE_OK)
        
    ###############
    # Callbacks
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
        
        parent = self.get_window()
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
        <menubar>
            <menu name="base_edit">
                <placeholder name="EditSearchMenu">
                    <separator />
                    <menuitem name="CulebraFindToggle"
                        action="%s" />
                    <menuitem name="CulebraReplaceToggle"
                        action="%s" />
                </placeholder>
            </menu>
        </menubar>
        <toolbar>
            <placeholder name="ProjectToolbar">
                <separator />
                <toolitem name="CulebraFindToggle"
                action="%s" />
                <toolitem name="CulebraReplaceToggle"
                action="%s" />
            </placeholder>
        </toolbar>
        """ % (common.ACTION_FIND_TOGGLE, common.ACTION_REPLACE_TOGGLE,
              common.ACTION_FIND_TOGGLE, common.ACTION_REPLACE_TOGGLE)
    
    ####################################
    # gtk.Action's definition
    @actions.action(
        name = common.ACTION_FIND_TOGGLE,
        stock_id = gtk.STOCK_FIND,
        label = "_Find...",
        type = actions.TYPE_TOGGLE,
        default_accel = '<Shift><Control>f'
    )
    def act_find_toggle(self, action):
        """Search for text"""
    
    @actions.action(
        name = common.ACTION_REPLACE_TOGGLE,
        stock_id = gtk.STOCK_FIND_AND_REPLACE,
        label = "_Replace...",
        type = actions.TYPE_TOGGLE,
        default_accel = '<Shift><Control>r'
    )
    def act_replace_toggle(self, action):
        """Search and replace text"""
    
    @actions.action(
        name = common.ACTION_FIND_FORWARD,
        stock_id = gtk.STOCK_GO_FORWARD,
        default_accel = '<Control>g'
    )
    def act_find_forward(self, action):
        """Find next matching word"""
    
    @actions.action(
        name = common.ACTION_FIND_BACKWARD,
        stock_id = gtk.STOCK_GO_BACK,
        default_accel = '<Control><Shift>g'
        
    )
    def act_find_backward(self, action):
        """Find previous mathing word"""

    @actions.action(
        name = common.ACTION_REPLACE_FORWARD,
        stock_id = gtk.STOCK_GO_FORWARD,
    )
    def act_replace_forward(self, action):
        """Replaces the next matching word"""

    @actions.action(
        name = common.ACTION_REPLACE_BACKWARD,
        stock_id = gtk.STOCK_GO_BACK,
    )
    def act_replace_backward(self, action):
        """Replaces backward"""
    
    @actions.action(
        name = common.ACTION_REPLACE_ALL,
        stock_id = gtk.STOCK_FIND_AND_REPLACE,
        label = "Replace Alll"
    )
    def act_replace_all(self, action):
        """Replaces all matching words"""
        


Service = culebra_editor
