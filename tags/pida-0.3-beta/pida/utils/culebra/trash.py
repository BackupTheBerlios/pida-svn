class GotoLineComponent(ChildObject):
    # This class is probably going to be moved elsewhere
    def __init__(self, parent, action):
        super(GotoLineComponent, self).__init__(parent)
        self.action = action
        self._dialog = None
        self.action.connect("activate", self.on_goto_line)
    
    def create_dialog(self):
        dialog = gtk.Dialog("", self.parent.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                           (gtk.STOCK_JUMP_TO, RESPONSE_FORWARD))

        hide_on_delete(dialog)
        dialog.connect("response", self.on_dialog_response)
        dialog.connect("key-release-event", self.key_release_callback)
        dialog.set_default_response(RESPONSE_FORWARD)
        dialog.set_border_width(12)
        dialog.set_has_separator(False)
        dialog.action_area.set_border_width(0)
        
        hbox = gtk.HBox()
        hbox.show()
        hbox.set_spacing(6)
        dialog.vbox.add(hbox)
        
        lbl = gtk.Label()
        lbl.set_markup_with_mnemonic("_Line number:")
        lbl.show()
        hbox.pack_start(lbl, False, False)
        
        line_text = gtk.Entry()
        self.line_text = line_text
        line_text.set_activates_default(True)
        line_text.connect("changed", self.on_text_changed)
        line_text.show()
        hbox.pack_start(line_text, False, False)
        
        self.on_text_changed(self.line_text)
        
        return dialog
    
    def get_dialog(self):
        if dialog is None:
            self._dialog = self.create_dialog()
        return self._dialog
    
    dialog = property(get_dialog)
    
    def on_dialog_response(self, dialog, response_id):
        if response_id == gtk.RESPONSE_CLOSE:
            dialog.hide()
            return

        line = self.line_text.get_text()
        if not line.isdigit():
            return
            
        buff = self.get_parent().get_buffer()
        titer = buff.get_iter_at_line(int(line)-1)
        self.get_parent().scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)
        
        # hide when we find something
        self.get_parent().grab_focus()
        dialog.hide()
    
    def on_text_changed(self, entry):
        is_sensitive = self.line_text.get_text().isdigit()
        self.dialog.set_response_sensitive(RESPONSE_FORWARD, is_sensitive)
    
    def on_goto_line(self, edit_window):
        self.line_text.select_region(0, -1)
        self.line_text.grab_focus()
       
        self.dialog.show()
        self.line_text.grab_focus()

    def key_release_callback(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.dialog.hide()




 





class EditWindow(binding.Component, gtk.EventBox):
    # XXX: THIS CLASS IS SOOOO DEAD!!!111oneone!
     
    # If the user access the event sources, the 'events' field is created
    # and vice-versa
    _buffer_changed = binding.Make(
        lambda self: self.events.create_event("buffer-changed")
    )
    
    _buffer_closed = binding.Make(
        lambda self: self.events.create_event("buffer-changed")
    )
    
    def events(self):
        events = EventsDispatcher()
        self._buffer_changed = events.create_event("buffer-changed")
        self._buffer_closed  = events.create_event("buffer-closed-event")
        return events
        
    events = binding.Make(events, uponAssembly = True)
    
    search_bar = binding.Make(SearchBar)
    replace_bar = binding.Make(ReplaceBar)
    def __init__(self, plugin=None, quit_cb=None):
        gtk.EventBox.__init__(self)
        
        self.plugin = plugin
        self.entries = BufferManager()
        
        self.completion_window = None
        self.set_size_request(470, 300)
        self.connect("delete_event", self.file_exit)
        self.quit_cb = quit_cb
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()
        self.menubar, self.toolbar = self.create_menu()
        
        self.vbox.pack_start(self.menubar, expand=False)
        self.menubar.show()
        
        hdlbox = gtk.HandleBox()
        self.vbox.pack_start(hdlbox, expand=False)
        hdlbox.show()
        hdlbox.add(self.toolbar)
        self.toolbar.show()
        
        self.vpaned = gtk.VPaned()
        self.vbox.pack_start(self.vpaned, expand=True, fill = True)
        self.vpaned.show()
        self.vbox1 = gtk.VBox()
        self.vpaned.add1(self.vbox1)
        self.vbox.show()
        self.vbox1.show()
        self.hpaned = gtk.HPaned()
        self.vbox1.pack_start(self.hpaned, True, True)
        self.hpaned.set_border_width(5)
        self.hpaned.show()
        
        # the gtksourceview
        self.editor = CulebraView()
        self.plugin.pida.mainwindow.connect('delete-event', self.file_exit)
        self.scrolledwin = gtk.ScrolledWindow()
        self.scrolledwin.add(self.editor)
        self.editor.connect('key-press-event', self.text_key_press_event_cb)
        self.scrolledwin.show()
        self.editor.show()
        self.editor.grab_focus()
        
        vbox = gtk.VBox(spacing = 6)
        vbox.show()
        vbox.add(self.scrolledwin)
        vbox.pack_start(self.search_bar.widget, expand = False, fill = False)
        vbox.pack_start(self.replace_bar.widget, expand = False, fill = False)
        
        self.hpaned.add2(vbox)
        self.hpaned.set_position(200)
        self.dirty = 0
        self.clipboard = gtk.Clipboard(selection='CLIPBOARD')
        self.dirname = "."
        # sorry, ugly
        self.filetypes = {}
        
        binding.Component.__init__(self)
    
    def create_menu(self):
        ui_string = """<ui>
        <menubar>
                <menu name='FileMenu' action='FileMenu'>
                        <menuitem action='FileNew'/>
                        <menuitem action='FileOpen'/>
                        <separator/>
                        <menuitem action='FileSave'/>
                        <menuitem action='FileSaveAs'/>
                        <menuitem action='FileRevert'/>
                        <separator/>
                        <menuitem action='PrevBuffer'/>
                        <menuitem action='NextBuffer'/>
                        <menuitem action='Close'/>
                        <menuitem action='FileExit'/>
                </menu>
                <menu name='EditMenu' action='EditMenu'>
                        <menuitem action='EditUndo'/>
                        <menuitem action='EditRedo'/>
                        <separator/>
                        <menuitem action='EditCut'/>
                        <menuitem action='EditCopy'/>
                        <menuitem action='EditPaste'/>
                        <separator/>
                        <menuitem action='DuplicateLine'/>
                        <menuitem action='DeleteLine'/>
                        <menuitem action='CommentBlock'/>
                        <menuitem action='UncommentBlock'/>
                        <menuitem action='UpperSelection'/>
                        <menuitem action='LowerSelection'/>
                        <separator/>
                        <menuitem action='Configuration' />
                </menu>
                <menu name='FindMenu' action='FindMenu'>
                        <menuitem action='EditFind'/>
                        <menuitem action='EditFindNext'/>
                        <menuitem action='EditReplace'/>
                        <separator/>                        
                        <menuitem action='GotoLine'/>
                </menu>
                <menu name='RunMenu' action='RunMenu'>
                        <menuitem action='RunScript'/>
                        <menuitem action='StopScript'/>
                        <menuitem action='DebugScript'/>
                        <menuitem action='DebugStep'/>
                        <menuitem action='DebugNext'/>
                        <menuitem action='DebugContinue'/>
                </menu>
                <menu name='HelpMenu' action='HelpMenu'>
                        <menuitem action='About'/>
                </menu>
        </menubar>
        <toolbar>
                <toolitem action='FileNew'/>
                <toolitem action='FileOpen'/>
                <toolitem action='FileSave'/>
                <separator/>
                <toolitem action='EditUndo'/>
                <toolitem action='EditRedo'/>
                <separator/>
                <toolitem action='EditCut'/>
                <toolitem action='EditCopy'/>
                <toolitem action='EditPaste'/>
                <separator/>
                <toolitem action='EditFind'/>
                <toolitem action='EditReplace'/>
                <separator/>
                <toolitem action='RunScript'/>
        </toolbar>
        </ui>
        """
        actions = [
           ('FileMenu', None, '_File'),
           ('FileNew', gtk.STOCK_NEW, None, None, "Create a new file", self.file_new),
           ('FileOpen', gtk.STOCK_OPEN, None, None, "Open a file", self.file_open),
           ('FileSave', gtk.STOCK_SAVE, None, None, "Save current file", self.file_save),
           ('FileSaveAs', gtk.STOCK_SAVE_AS, None, None, "Save the current file with a different name",
             self.file_saveas),
           ('FileRevert', gtk.STOCK_REVERT_TO_SAVED, None, None, "Revert to a saved version of the file", self.file_revert),
           ('PrevBuffer', gtk.STOCK_GO_UP, None, "<control>Page_Up","Previous buffer", self.prev_buffer),
           ('NextBuffer', gtk.STOCK_GO_DOWN, None, "<control>Page_Down","Next buffer", self.next_buffer),           ('Close', gtk.STOCK_CLOSE, None, None, "Close current file", self.file_close),
           ('FileExit', gtk.STOCK_QUIT, None, None, None, self.file_exit),
           ('EditMenu', None, '_Edit'),
           ('EditUndo', gtk.STOCK_UNDO, None, "<control>z", "Undo the last action", self.edit_undo),
           ('EditRedo', gtk.STOCK_REDO, None, "<control><shift>z", "Redo the undone action" , self.edit_redo),
           ('EditCut', gtk.STOCK_CUT, None, None, "Cut the selection", self.edit_cut),
           ('EditCopy', gtk.STOCK_COPY, None, None, "Copy the selection", self.edit_copy),
           ('EditPaste', gtk.STOCK_PASTE, None, None, "Paste the clipboard", self.edit_paste),
           ('EditClear', gtk.STOCK_REMOVE, 'C_lear', None, None,
             self.edit_clear),
           ('Configuration', gtk.STOCK_PREFERENCES, None, None, None,
                lambda action: self.plugin.do_action('showconfig', 'culebra')),
            
            ('DuplicateLine', None, 'Duplicate Line', '<control>d', 
                 None, self.duplicate_line),
            ('DeleteLine', None, 'Delete Line', '<control>y', 
                 None, self.delete_line),
            ('CommentBlock', None, 'Comment Selection', '<control>k', 
                 None, self.comment_block),
            ('UncommentBlock', None, 'Uncomment Selection', '<control><shift>k', 
                 None, self.uncomment_block),
            ('UpperSelection', None, 'Upper Selection Case', '<control>u', 
                 None, self.upper_selection),
            ('LowerSelection', None, 'Lower Selection Case', '<control><shift>u', 
                 None, self.lower_selection),
           ('FindMenu', None, '_Search'),
           ('EditFindNext', gtk.STOCK_FIND, 'Find Forward', 'F3', None, self.edit_find_next),
           ('EditFindBack', gtk.STOCK_FIND, 'Find Backwards', None, None, self.edit_find_back),
           ('EditReplaceNext', gtk.STOCK_FIND_AND_REPLACE, "_Replace", None, "Replace text and find next", None),
           ('EditReplaceAll', gtk.STOCK_FIND_AND_REPLACE, "_Replace All", None,  "Replace all entries", None),
           ('GotoLine', gtk.STOCK_JUMP_TO, 'Goto Line', '<control>g', None, None),
           ('RunMenu', None, '_Run'),
           ('RunScript', gtk.STOCK_EXECUTE, None, "F5","Run script", self.run_script),
           ('StopScript', gtk.STOCK_STOP, None, "<ctrl>F5","Stop script execution", self.stop_script),
           ('DebugScript', None, "Debug Script", "F7",None, self.debug_script),
           ('DebugStep', None, "Step", "F8",None, self.step_script),
           ('DebugNext', None, "Next", "<shift>F7",None, self.next_script),
           ('DebugContinue', None, "Continue", "<control>F7", None, self.continue_script),
           ('BufferMenu', None, '_Buffers'),
           ('HelpMenu', None, '_Help'),
           ('About', gtk.STOCK_ABOUT, None, None, None, self.about),
            ]
        self.ag = gtk.ActionGroup('edit')
        self.ag.add_actions(actions)
        self.ag.add_toggle_actions((
           ('EditFind', gtk.STOCK_FIND, "Find...", None, "Search for text", None),
           ('EditReplace', gtk.STOCK_FIND_AND_REPLACE, "_Replace...", '<control>h', 
                "Search for and replace text", None),
        ))
        for action_name in("FileOpen", "FileSave", "EditUndo", "RunScript"):
            action = self.ag.get_action(action_name)
            action.set_property("is-important", True)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(self.ag, 0)
        self.ui.add_ui_from_string(ui_string)
        
        toolbar = self.ui.get_widget("/toolbar")
        toolbar.set_property("show-arrow", False)
        
        self.get_parent_window().add_accel_group(self.ui.get_accel_group())
        return(self.ui.get_widget('/menubar'), toolbar)
    
    __use_autocomplete = False
    def get_use_autocomplete(self):
        return self.__use_autocomplete
    
    def set_use_autocomplete(self, value):
        self.__use_autocomplete = value
    
    use_autocomplete = property(get_use_autocomplete, set_use_autocomplete)
    
    def about(self, mi):
        d = gtk.AboutDialog()
        d.set_name('Culebra Editor')
        d.set_version('0.2.3')
        d.set_copyright('Copyright © 2005 Fernando San Martín Woerner')
        d.set_comments('This plugin works as a text editor inside PIDA')
        d.set_authors(['Fernando San Martín Woerner(fsmw@gnome.org)',
                        'Ali Afshar(aafshar@gmail.com) ',
                        'Tiago Cogumbreiro(cogumbreiro@users.sf.net)'])
        d.show()

    def set_title(self, title):
        self.plugin.pida.mainwindow.set_title(title)

    def get_parent_window(self):
        return self.plugin.pida.mainwindow

    def get_current(self):
        return self.entries.selected
    
    def get_context(self, buff, it, sp=False):
        iter2 = it.copy()
        if sp:
            it.backward_word_start()
        else:
            it.backward_word_starts(1)
        iter3 = it.copy()
        iter3.backward_chars(1)
        prev = iter3.get_text(it)
        complete = it.get_text(iter2)
        self.context_bounds =(buff.create_mark('cstart',it), buff.create_mark('cend',iter2))
        if prev in(".", "_"):
            t = self.get_context(buff, it)
            return t + complete
        else:
            count = 0
            return complete

    def text_key_press_event_cb(self, widget, event):
        #print event.state, event.keyval
        keyname = gtk.gdk.keyval_name(event.keyval)
        buf = widget.get_buffer()
        bound = buf.get_selection_bounds()
        tabs = widget.get_tabs_width()
        space = " ".center(tabs)
        # shift-tab unindent
        if event.state & gtk.gdk.SHIFT_MASK and keyname == "ISO_Left_Tab":
            if len(bound) == 0:
                it = buf.get_iter_at_mark(buf.get_insert())
                start = buf.get_iter_at_line(it.get_line())
                end = buf.get_iter_at_line(it.get_line())
                count = 0
                while end.get_char() == " " and count < tabs:
                    end.forward_char()
                    count += 1
                buf.delete(start, end)
            else:
                start, end = bound
                start_line = start.get_line()
                end_line = end.get_line()
                while start_line <= end_line:
                    insert_iter = buf.get_iter_at_line(start_line)
                    if not insert_iter.ends_line():
                        s_it = buf.get_iter_at_line(start_line)
                        e_it = buf.get_iter_at_line(start_line)
                        count = 0
                        while e_it.get_char() == " " and count < tabs:
                            e_it.forward_char()
                            count += 1
                        buf.delete(s_it, e_it)        
                    start_line += 1
            return True
        #tab indent
        elif event.keyval == gtk.keysyms.Tab:
            if len(bound) == 0:
                buf.insert_at_cursor(space)
            else:
                start, end = bound
                start_line = start.get_line()
                end_line = end.get_line()
                while start_line <= end_line:
                    insert_iter = buf.get_iter_at_line(start_line)
                    if not insert_iter.ends_line():
                        buf.insert(insert_iter, space)
                    start_line += 1
            return True

    def load_file(self, fname):
        buff = None
        
        for ent in self.entries:
            if ent.filename == fname:
               buff = ent
               break
        
        if buff is None:
            new_entry = True
            buff = CulebraBuffer()
            buff.filename = fname
            # We only update the contents of a new buffer
            try:
                fd = open(fname)
                buff.begin_not_undoable_action()
                buff.set_text('')
                data = fd.read()
                enc_data = None
                for enc in(sys.getdefaultencoding(), "utf-8", "iso8859", "ascii"):
                    try:
                        enc_data = unicode(data, enc)
                        buff.encoding = enc
                        break
                    except UnicodeDecodeError:
                        pass
                assert enc_data is not None, "There was a problem detecting the encoding"
                    
                
                buff.set_text(enc_data)
                buff.set_modified(False)
                buff.place_cursor(buff.get_start_iter())
                buff.end_not_undoable_action()
                fd.close()

                self.check_mime(buff)

                self.set_title(os.path.basename(fname))
                self.dirname = os.path.dirname(fname)
                
            except:
                dlg = gtk.MessageDialog(self.get_parent_window(),
                        gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                        "Can't open " + fname)
                import traceback
                traceback.print_exc()
                
                print sys.exc_info()[1]
                resp = dlg.run()
                dlg.hide()
                return
            self.entries.append(buff)

        else:
            new_entry = False
            
            
        # Replace a not modified new buffer when we open
        if new_entry and self.entries.count_new() == 1 and len(self.entries) == 2:
            if self.entries[0].is_new:
                new_entry = self.entries[0]
            else:
                new_entry = self.entries[1]
            
            if not new_entry.get_modified():
                # Remove the new entry
                self.entries.remove(new_entry)
                    
        self.editor.grab_focus()

    def check_mime(self, buff):
        manager = buff.languages_manager
        if os.path.isabs(buff.filename):
            path = buff.filename
        else:
            path = os.path.abspath(buff.filename)
        uri = gnomevfs.URI(path)

        mime_type = gnomevfs.get_mime_type(path) # needs ASCII filename, not URI
        if mime_type:
            language = manager.get_language_from_mime_type(mime_type)
            if language is not None:
                buff.set_highlight(True)
                buff.set_language(language)
            else:
                dlg = gtk.MessageDialog(self.get_parent_window(),
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                    'No language found for mime type "%s"' % mime_type)
                buff.set_highlight(False)
        else:
            dlg = gtk.MessageDialog(self.get_parent_window(),
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                    'Couldn\'t get mime type for file "%s"' % fname)
            buff.set_highlight(False)


    def chk_save(self):
        buff = self.get_current()

        if buff.get_modified():
            dlg = gtk.Dialog('Unsaved File', self.get_parent_window(),
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_YES, gtk.RESPONSE_YES,
                          gtk.STOCK_NO, gtk.RESPONSE_NO,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            lbl = gtk.Label((buff.is_new and "Untitled" or buff.filename)+
                        " has not been saved\n" +
                        "Do you want to save it?")
            lbl.show()
            dlg.vbox.pack_start(lbl)
            ret = dlg.run()
            dlg.hide()
            if ret == gtk.RESPONSE_NO:
                return False
            if ret == gtk.RESPONSE_YES:
                if self.file_save():
                    return False
            return True
        return False

    def file_new(self, mi=None):
        buff = CulebraBuffer()
        buff.set_text("")
        buff.set_modified(False)

        manager = buff.languages_manager
        language = manager.get_language_from_mime_type("text/x-python")
        buff.set_highlight(True)
        buff.set_language(language)

        self.entries.append(buff)

        self.plugin.do_edit('changebuffer', len(self.entries) - 1)

    def file_open(self, mi=None):
            
        fn = self.get_current().filename
        dirn = os.path.dirname(fn)
        fname = dialogs.OpenFile('Open File', self.get_parent_window(),
                                  dirn, None, "*.py")
        
        if fname is None:
            return
        
        first_entry = self.entries[0]
        new_and_changed = first_entry.is_new and first_entry.get_modified()
        
        if len(self.entries) == 1 and new_and_changed and self.chk_save():
            return
            
        self.load_file(fname)
        self.plugin.pida.mainwindow.set_title(os.path.split(fname)[1])

    def file_save(self, mi=None, fname=None):
            
        buff = self.get_current()
        if buff.is_new:
            return self.file_saveas()
            
        curr_mark = buff.get_iter_at_mark(buff.get_insert())
        f = buff.filename
        ret = False
        if fname is None:
            fname = f
        try:
            start, end = buff.get_bounds()
            blockend = start.copy()
            #XXX: this is not safe, we should write to a temporary filename
            #XXX: and when it's finished we should delete the original
            #XXX: and swap filenames
            fd = open(fname, "w")

            writer = codecs.getwriter(buff.encoding)(fd)
            
            while blockend.forward_chars(BLOCK_SIZE):
                data = buff.get_text(start, blockend).decode("utf-8")
                writer.write(data)
                start = blockend.copy()

            data = buff.get_text(start, blockend).decode("utf-8")
            writer.write(data)

            fd.close()
            buff.set_modified(False)
            buff.filename = fname
            self.plugin.pida.mainwindow.set_title(os.path.split(fname)[1])
            ret = True
        except:
            dlg = gtk.MessageDialog(self.get_parent_window(),
                                gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                "Error saving file " + fname)
            print sys.exc_info()[1]
            resp = dlg.run()
            dlg.hide()
            ret = False

        self.check_mime(self.entries.selected)
        buff.place_cursor(curr_mark)
        self.editor.grab_focus()
        return ret

    def file_saveas(self, mi=None):
        #XXX: When a user saves the file with an already opened file
        #XXX: we get two buffers pointing to the same file.
        buff = self.get_current()
        f = dialogs.SaveFile('Save File As', 
                                self.get_parent_window(), 
                                self.dirname,
                                buff.filename)
        if not f: return False
        self.dirname = os.path.dirname(f)
        self.plugin.pida.mainwindow.set_title(os.path.basename(f))
        buff.filename = f
            
        return self.file_save(fname=f)
    
    def file_revert(self, *args):
        # XXX: the save dialog is totally inapropriate, should be a revert dialog
        self.chk_save()
        self.load_file(self.get_current().filename)
    
    def file_close(self, mi=None, event=None):
        self.chk_save()
        del self.entries.selected
        self._buffer_closed()

    def file_exit(self, mi=None, event=None):
        if self.chk_save(): return True
        self.hide()
        self.destroy()
        if self.quit_cb: self.quit_cb(self)
        self.plugin.do_action('quit')
        return False

    def edit_cut(self, mi):
        self.get_current().cut_clipboard(self.clipboard, True)
        return

    def edit_copy(self, mi):
        self.get_current().copy_clipboard(self.clipboard)
        return

    def edit_paste(self, mi):
        self.get_current().paste_clipboard(self.clipboard, None, True)
        return

    def edit_clear(self, mi):
        self.get_current().delete_selection(True, True)
        return
        
    def edit_undo(self, mi):
        self.get_current().undo()
        
    def edit_redo(self, mi):
        self.get_current().redo()
    
    def focus_line(self):
        buff = self.get_current()
        mark = buff.get_insert()
        line_iter = buff.get_iter_at_mark(mark)
        self.editor.scroll_to_iter(line_iter, 0.25)        
    
    def find(self, find_forward):
        buff = self.get_current()
        found = buff.search(find_forward = find_forward)

        if not found and len(buff.get_selection_bounds()) == 0:
            found = buff.search(find_forward = not find_forward)

        if not found:
            return
            
        mark = buff.get_insert()
        line_iter = buff.get_iter_at_mark(mark)
        self.editor.scroll_to_iter(line_iter, 0.25)
    
    def edit_find_next(self, action = None):
        self.find(find_forward = True)
    
    def edit_find_back(self, action = None):
        self.find(find_forward = False)
        
    def comment_block(self, mi=None):
        comment = "#"
        buf = self.get_current()
        bound = buf.get_selection_bounds()
        if len(bound) == 0:
            it = buf.get_iter_at_mark(buf.get_insert())
            line = it.get_line()
            insert_iter = buf.get_iter_at_line(line)
            buf.insert(insert_iter, comment)
        else:
            start, end = bound
            start_line = start.get_line()
            end_line = end.get_line()
            while start_line <= end_line:
                insert_iter = buf.get_iter_at_line(start_line)
                if not insert_iter.ends_line():
                    buf.insert(insert_iter, comment)
                start_line += 1
   
    def uncomment_block(self, mi=None):
        buf = self.get_current()
        bound = buf.get_selection_bounds()
        if len(bound) == 0:
            it = buf.get_iter_at_mark(buf.get_insert())
            start = buf.get_iter_at_line(it.get_line())
            end = buf.get_iter_at_line(it.get_line())
            count = 0
            while end.get_char() == "#":
                end.forward_char()
                count += 1
            buf.delete(start, end)
        else:
            start, end = bound
            start_line = start.get_line()
            end_line = end.get_line()
            while start_line <= end_line:
                insert_iter = buf.get_iter_at_line(start_line)
                if not insert_iter.ends_line():
                    s_it = buf.get_iter_at_line(start_line)
                    e_it = buf.get_iter_at_line(start_line)
                    count = 0
                    while e_it.get_char() == "#":
                        e_it.forward_char()
                        count += 1
                    buf.delete(s_it, e_it)        
                start_line += 1
                
    def delete_line(self, mi):
        buf = self.get_current()
        it = buf.get_iter_at_mark(buf.get_insert())
        line = it.get_line()
        start = buf.get_iter_at_line(line)
        end = buf.get_iter_at_line(line+1)
        if start.get_line() == end.get_line():
            end.forward_to_end()
        buf.delete(start, end)
            
    def duplicate_line(self, mi):
        buf = self.get_current()
        it = buf.get_iter_at_mark(buf.get_insert())
        line = it.get_line()
        start = buf.get_iter_at_line(line)
        end = buf.get_iter_at_line(line+1)
        ret = ""
        if start.get_line() == end.get_line():
            end.forward_to_end()
            ret = "\n"
        text = buf.get_text(start, end)
        buf.insert(end, ret+text)
    
    def upper_selection(self, mi):
        buf = self.get_current()
        bound = buf.get_selection_bounds()
        if not len(bound) == 0:
            start, end = bound
            text = buf.get_text(start, end)
            buf.delete(start, end)
            buf.insert(start, text.upper())
            
    def lower_selection(self, mi):
        buf = self.get_current()
        bound = buf.get_selection_bounds()
        if not len(bound) == 0:
            start, end = bound
            text = buf.get_text(start, end)
            buf.delete(start, end)
            buf.insert(start, text.lower())
    
    def run_script(self, mi):
        self.file_save()
        self.plugin.do_evt("bufferexecute") 
        
    def stop_script(self, mi):
        self.plugin.do_evt('killterminal')
        
    def debug_script(self, mi):
        self.plugin.do_evt('debuggerload')
        buff = self.get_current()
        titer = buff.get_iter_at_line(0)
        self.editor.scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)
        
    def step_script(self, mi):
        self.plugin.do_evt('step')

    def next_script(self, mi):
        self.plugin.do_evt('next')

    def continue_script(self, mi):
        self.plugin.do_evt('continue')
        
    def next_buffer(self, mi):
        if self.entries.can_select_next():
            self.scrolledwin.freeze_child_notify()
            self.entries.select_next()
            self.plugin.edit_getbufferlist()            
            self.plugin.do_edit('changebuffer', self.entries.selected_index)
            self.scrolledwin.thaw_child_notify()

    def prev_buffer(self, mi):
        if self.entries.can_select_previous():
            self.scrolledwin.freeze_child_notify()
            self.entries.select_previous() 
            self.plugin.edit_getbufferlist()
            self.plugin.do_edit('changebuffer', self.entries.selected_index)
            self.scrolledwin.thaw_child_notify()

gobject.type_register(EditWindow)


class Cb:
    def __init__(self):
        self.mainwindow = None
        
def edit(fname, mainwin=False):
    quit_cb = lambda w: gtk.main_quit()
    cb = Cb()
    w = gtk.Window()
    w.connect('delete-event', gtk.main_quit)
    cb.mainwindow = w
    e = EditWindow(cb, quit_cb=quit_cb)
    if fname != "":
        w.file_new()
    w.set_title("Culebra")
    w.add(e)
    w.maximize()
    w.show_all()
    w.set_size_request(0,0)

    w.dirname = os.getcwd()

    if mainwin: gtk.main()
    return
