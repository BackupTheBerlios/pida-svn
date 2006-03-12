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
    'culebraedit+cut_line': (100 ,C),
    'culebraedit+select_line': (108 ,C),
    'culebraedit+select_word': (104 ,C),
    'culebraedit+cut_word': (106 ,C),
    'culebraedit+select_sentence': (105 ,C),
    'culebraedit+cut_sentence': (117 ,C),
    'culebraedit+select_paragraph': (112 ,C),
}

class culebra_view(contentview.content_view):

    HAS_CONTROL_BOX = False
    HAS_TITLE = False

    def init(self, filename=None, action_group=None, background_color=None,
                   font_color=None, font_text=None):
        self.widget.set_no_show_all(True)
        widget, editor = edit.create_widget(filename, action_group)
        editor.set_background_color(background_color)
        editor.set_font_color(font_color)
        editor.set_font(font_text)
        self.__editor = editor
        try:
            self.buffer.connect('can-undo', self.cb_can_undo)
            self.buffer.connect('can-redo', self.cb_can_redo)
        except TypeError:
            # In this case we are not dealling with sourceview
            pass
        widget.show()
        self.widget.add(widget)

    def get_editor(self):
        return self.__editor
        
    editor = property(get_editor)

    def get_buffer(self):
        return self.__editor.get_buffer()
        
    buffer = property(get_buffer)
    
    def can_undo(self):
        return self.buffer.can_undo()

    def can_redo(self):
        return self.buffer.can_redo()
    
    def cb_can_undo(self, buffer, can):
        self.service.cb_can_undo(self, can)
    
    def cb_can_redo(self, buffer, can):
        self.service.cb_can_redo(self, can)

    def connect_keys(self):
        self.__editor.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.__editor.connect('key-press-event', self.cb_keypress)

    def cb_keypress(self, widg, event):
        key, mod = event.keyval, event.state
        return self.service.received_key(key, mod)
        

class culebra_editor(service.service):

    display_name = 'Culebra Text Editor'

    class Culebra(defs.View):
        view_type = culebra_view
        book_name = 'edit'
    
    class general(defs.optiongroup):
        class background_color(defs.option):
            """Change the background color"""
            default = "#FFFFFF"
            rtype = types.color
        
        class font(defs.option):
            """Change the font used in Culebra."""
            rtype = types.font
            default = 'monospace 10'

        class font_color(defs.option):
            """Change the font color"""
            default = "#000000"
            rtype = types.color
            
    ############
    # Service related methods
    def init(self):
        self.__documents = {}
        self.__views = {}
        self.__keymods = {}
        self.__undoacts = {}
        self._save_action = None

    def reset(self):
        self.__bind_document_actions()
        for view in self.__views.values():
            view.editor.set_background_color(self.get_background_color())
            view.editor.set_font_color(self.get_font_color())
            view.editor.set_font(self.opt('general', 'font'))

    # private interface

    def __bind_document_actions(self):
        actions = self.boss.call_command("documenttypes", "get_document_actions")
        for action in actions:
            actname = action.get_name()
            if actname in KEYMAP:
                self.__keymods[KEYMAP[actname]] = action
            if actname == 'documenttypes+document+undo':
                self.__undoacts['undo'] = action
            elif actname == 'documenttypes+document+redo':
                self.__undoacts['redo'] = action
            elif actname == 'documenttypes+document+revert':
                self.__revertact = action
            elif actname == 'DocumentSave':
                self._save_action = action
        for act in self.action_group.list_actions():
            actname = act.get_name()
            if actname in KEYMAP:
                self.__keymods[KEYMAP[actname]] = act
        
    def __load_document(self, document):
        view = self.create_view('Culebra',
            filename=document.filename,
            action_group=self.action_group,
            background_color = self.get_background_color(),
            font_color = self.get_font_color(),
            font_text = self.opt('general', 'font')
        )
        self.__views[document.unique_id] = view
        self.__documents[view.unique_id] = document
        view.connect_keys()
        self.show_view(view=view)

    def __view_document(self, document):
        view = self.__views[document.unique_id]
        view.raise_page()
        # Use subscription pattern
        if self.current_view is not None:
            self.current_view.editor.set_action_group(None)
        self.current_view = view
        self.__set_action_sensitivities(document)

    def __set_action_sensitivities(self, document):
        save_action = self.get_save_action()
        if document.is_new:
            save_action.set_sensitive(True)
            self.__revertact.set_sensitive(False)
        else:
            buff = self.current_view.editor.get_buffer()
            self.current_view.editor.set_action_group(self.action_group)
            self.linker = sensitive.SaveLinker(buff, save_action)
            self.linker2 = sensitive.SaveLinker(buff, self.__revertact)
        # undo redo
        self.cb_can_undo(self.current_view, self.current_view.can_undo())
        self.cb_can_redo(self.current_view, self.current_view.can_redo())

    def get_background_color(self):
        color = self.opt("general", "background_color")
        return gdk.color_parse(color)
    
    def get_font_color(self):
        color = self.opt("general", "font_color")
        return gdk.color_parse(color)
    
    def get_save_action(self):
        #if self._save_action is None:
        #    self._get_actions()
        return self._save_action

    def get_window(self):
        return self.boss.get_main_window()

    # keyboard bindings
    
    def received_key(self, key, mod):
        if (key, mod) in self.__keymods:
            self.__keymods[key, mod].emit('activate')
            return True
        else:
            return False

    # Undo/redo

    def cb_can_undo(self, view, can):
        if view is self.current_view:
            self.__undoacts['undo'].set_sensitive(can)

    def cb_can_redo(self, view, can):
        if view is self.current_view:
            self.__undoacts['redo'].set_sensitive(can)

    #############
    # Commands
    current_view = None
    def cmd_edit(self, document):
        # temporary to preserve old filename behaviour
        #filename = document.filename
        #if self.current_view is not None:
        #    self.current_view.editor.set_action_group(None)
        if document.unique_id not in self.__views:
            self.__load_document(document)
        self.__view_document(document)
    
    def _file_op(self, oper, attr, label):
        try:
            getattr(oper, attr)()
            return True
        except IOError, err:
            hig.error("There was an error trying to %s the document" % label,
                      str(err), parent=self.get_window())
        return False

    def cmd_revert(self):
        if self.current_view is None:
            return
            
        buff = self.current_view.editor.get_buffer().get_file_ops()

        if buff.get_is_new():
            return
        
        # Ok the buffer is not new and exists
        reply = hig.ok_cancel(
            "Revert the document to saved contents",
            ("Even if your document was just saved it could be altered by a "
             "third party. By reverting to its real contents you will loose "
             "all the changes you've made so far."),
            parent = self.get_window(),
            ok_button = gtk.STOCK_REVERT_TO_SAVED,
        )
        if reply == gtk.RESPONSE_OK and self._file_op(buff, "load", "revert"):
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
        file_ops = self.current_view.buffer.get_file_ops()
        if self._file_op(file_ops, "save", "save"):
            self.boss.call_command('buffermanager', 'reset_current_document')

    def cmd_save_as(self, filename):
        buf = self.current_view.buffer.get_file_ops()
        old_filename = buf.get_filename()
        buf.set_filename(filename)
        if not self._file_op(buf, "save", "save"):
            buf.set_filename(old_filename)

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
    
    def cmd_close(self, document):
        view = self.__views[document.unique_id]
        #view = self.current_view
        self.close_view(view)
        self.current_view = None

    def cmd_can_close(self):
        buffs = [view.buffer for view in self.__views.values() if view.buffer.get_modified()]
        # If we have no buffers to save, go on
        if len(buffs) == 0:
            return True
            
        filenames = dict(map(lambda buff: (buff.filename, buff), buffs))
        parent = self.get_window()
        files, response = hig.save_changes(filenames.keys(), parent=parent)
        # Save the files that need to be saved
        errors = []
        for filename in files:
            # XXX: handle new files
            try:
                filenames[filename].save()
            except IOError, err:
                errors.append(filename)
        if len(errors) > 0:
            # XXX: handle errors
            pass
        return response in (gtk.RESPONSE_CLOSE, gtk.RESPONSE_OK)
        
    def cmd_select_line(self):
        buf = self.current_view.editor.get_buffer()
        si = buf.get_iter_at_mark(buf.get_insert())
        ei = si.copy()
        si.set_line_offset(0)
        ei.forward_line()
        buf.select_range(si, ei)
        
    def cmd_cut_line(self):
        self.cmd_select_line()
        self.cmd_cut()
        
    def cmd_select_word(self):
        buf = self.current_view.editor.get_buffer()
        si = buf.get_iter_at_mark(buf.get_insert())
        if si.inside_word():
            ei = si.copy()
            if not si.starts_word():
                si.backward_word_start()
            if not ei.ends_word():
                ei.forward_word_end()
            buf.select_range(si, ei)
            return True
        else:
            return False
                
    def cmd_cut_word(self):
        if self.cmd_select_word():
            self.cmd_cut()
            
    def cmd_select_sentence(self):      
        buf = self.current_view.editor.get_buffer()
        si = buf.get_iter_at_mark(buf.get_insert())
        if si.inside_sentence():
            ei = si.copy()
            if not si.starts_sentence():
                si.backward_sentence_start()
            if not ei.ends_sentence():
                ei.forward_sentence_end()
            buf.select_range(si, ei)
            return True
        else:
            return False
            
    def cmd_cut_sentence(self):
        if self.cmd_select_sentence():
            self.cmd_cut()
    
    def cmd_select_paragraph(self):
        buf = self.current_view.editor.get_buffer()
        si = buf.get_iter_at_mark(buf.get_insert())
        if not si.get_chars_in_line() > 1:
            return
        ei = si.copy()
        while si.get_chars_in_line() > 1 and not si.is_start():
            si.backward_line()
            si.set_line_offset(0)
        if not si.is_start():
            si.forward_lines(1)
        while ei.get_chars_in_line() > 1 and not ei.is_end():
            ei.forward_line()
        buf.select_range(si, ei)
        
    ###############
    # Callbacks
    def view_closed(self, view):
        if view.unique_id in self.__documents:
            doc = self.__documents[view.unique_id]
            del self.__documents[view.unique_id]
            del self.__views[doc.unique_id]
            self.boss.call_command('buffermanager', 'document_closed',
                                   document=doc)

    def view_confirm_close(self, view):
        buff = view.buffer
        
        # If buffer was not modified you can safely close it
        if not buff.get_modified():
            return True
        
        # When the buffer is new then we need to show the save dialog instead
        # of a save changes dialog:
        if buff.get_file_ops().get_is_new():
            # XXX: this is utterly broken but there's no support for new files
            # either
            # well, there is now
            return True
        
        parent = self.get_window()
        files, response = hig.save_changes(
            [buff.filename],
            parent=parent
        )
        
        if response == gtk.RESPONSE_OK:
            if not self._file_ops(buff.get_file_ops(), "save", "save"):
                return False

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
        default_accel = '<Control>f'
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
    
    def act_select_line(self, action):
        self.cmd_select_line()
    
    def act_cut_line(self, action):
        self.cmd_cut_line()
    
    def act_select_word(self, action):
        self.cmd_select_word()
        
    def act_cut_word(self, action):
        self.cmd_cut_word()

    def act_select_sentence(self, action):
        self.cmd_select_sentence()
        
    def act_cut_sentence(self, action):
        self.cmd_cut_sentence()
        
    def act_select_paragraph(self, action):
        self.cmd_select_paragraph()
        

Service = culebra_editor
