# -*- coding: utf-8 -*-
# Copyright Fernando San Martín Woerner <fsmw@gnome.org>
# $Id$
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# This file is part of Culebra project.

import gtk
import sys, os
import pango
import dialogs
import gtksourceview
import gnomevfs
import importsTipper
import words

BLOCK_SIZE = 2048

special_chars = (".",)
RESPONSE_FORWARD = 0
RESPONSE_BACKWARD = 1
RESPONSE_REPLACE = 2

global newnumber
newnumber = 1

class EditWindow(gtk.EventBox):

    def __init__(self, cb, plugin=None, quit_cb=None):
        self.cb = cb
        gtk.EventBox.__init__(self)
        self.search_string = None
        self.last_search_iter = None
        self.completion_win = None
        self.insert_string = None
        self.cursor_iter = None
        self.plugin = plugin
        self.wins = {}
        self.current_word = ""
        self.wl = []
        self.ac_w = None
        self.set_size_request(470, 300)
        self.connect("delete_event", self.file_exit)
        self.quit_cb = quit_cb
        self.vbox = gtk.VBox()
        self.add(self.vbox)
        self.vbox.show()
        self.menubar, self.toolbar = self.create_menu()
        hdlbox = gtk.HandleBox()
        self.vbox.pack_start(hdlbox, expand=False)
        hdlbox.show()
        hdlbox.add(self.menubar)
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
        self.statusbar = gtk.Statusbar()
        self.vbox1.pack_start(self.statusbar, False, True)
        self.statusbar.show()
        self.scrolledwin2 = gtk.ScrolledWindow()
        self.scrolledwin2.show()
        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_scrollable(True)
        self.hpaned.add2(self.notebook)
        self.hpaned.set_position(200)
        self.notebook.show()
        self.notebook.connect('switch-page', self.switch_page_cb)
        self.dirty = 0
        self.clipboard = gtk.Clipboard(selection='CLIPBOARD')
        self.dirname = "."
        self.browser_menu = gtk.Menu()
        refresh_item = gtk.MenuItem("Refresh")
        self.browser_menu.append(refresh_item)
        refresh_item.show()
        refresh_item.connect("activate", self.refresh_browser)
        # sorry, ugly
        self.filetypes = {}
        return
        
    def create_menu(self):
        ui_string = """<ui>
        <menubar>
                <menu name='FileMenu' action='FileMenu'>
                        <menuitem action='FileNew'/>
                        <menuitem action='FileOpen'/>
                        <menuitem action='FileSave'/>
                        <menuitem action='FileSaveAs'/>
                        <menuitem action='Close'/>
                        <separator/>
                        <menuitem action='FileExit'/>
                </menu>
                <menu name='EditMenu' action='EditMenu'>
                        <menuitem action='EditCut'/>
                        <menuitem action='EditCopy'/>
                        <menuitem action='EditPaste'/>
                        <menuitem action='EditClear'/>
                        <separator/>
                        <menuitem action='EditFind'/>
                        <menuitem action='EditFindNext'/>
                        <menuitem action='EditReplace'/>
                        <separator/>
                        <menuitem action='DuplicateLine'/>
                        <menuitem action='DeleteLine'/>
                        <menuitem action='GotoLine'/>
                        <menuitem action='CommentBlock'/>
                        <menuitem action='UncommentBlock'/>
                        <menuitem action='UpperSelection'/>
                        <menuitem action='LowerSelection'/>
                </menu>
                <menu name='RunMenu' action='RunMenu'>
                        <menuitem action='RunScript'/>
                        <menuitem action='DebugScript'/>
                        <menuitem action='DebugStep'/>
                        <menuitem action='DebugNext'/>
                        <menuitem action='DebugContinue'/>
                </menu>
        </menubar>
        <toolbar>
                <toolitem action='FileNew'/>
                <toolitem action='FileOpen'/>
                <toolitem action='FileSave'/>
                <toolitem action='FileSaveAs'/>
                <toolitem action='Close'/>
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
            ('FileNew', gtk.STOCK_NEW, None, None, None, self.file_new),
            ('FileOpen', gtk.STOCK_OPEN, None, None, None, self.file_open),
            ('FileSave', gtk.STOCK_SAVE, None, None, None, self.file_save),
            ('FileSaveAs', gtk.STOCK_SAVE_AS, None, None, None,
             self.file_saveas),
            ('Close', gtk.STOCK_CLOSE, None, None, None, self.file_close),
            ('FileExit', gtk.STOCK_QUIT, None, None, None, self.file_exit),
            ('EditMenu', None, '_Edit'),
            ('EditCut', gtk.STOCK_CUT, None, None, None, self.edit_cut),
            ('EditCopy', gtk.STOCK_COPY, None, None, None, self.edit_copy),
            ('EditPaste', gtk.STOCK_PASTE, None, None, None, self.edit_paste),
            ('EditClear', gtk.STOCK_REMOVE, 'C_lear', None, None,
             self.edit_clear),
            ('EditFind', gtk.STOCK_FIND, None, None, None, self.edit_find),
            ('EditFindNext', None, 'Find _Next', None, None, self.edit_find_next),
            ('EditReplace', gtk.STOCK_FIND_AND_REPLACE, 'Replace', '<control>h', 
                None, self.edit_replace),
             ('DuplicateLine', None, 'Duplicate Line', '<control>d', 
                 None, self.duplicate_line),
             ('DeleteLine', None, 'Delete Line', '<control>y', 
                 None, self.delete_line),
             ('GotoLine', None, 'Goto Line', '<control>g', 
                 None, self.goto_line),
             ('CommentBlock', None, 'Comment Selection', '<control>k', 
                 None, self.comment_block),
             ('UncommentBlock', None, 'Uncomment Selection', '<control><shift>k', 
                 None, self.uncomment_block),
             ('UpperSelection', None, 'Upper Selection', '<control>u', 
                 None, self.upper_selection),
             ('LowerSelection', None, 'Lower Selection', '<control><shift>u', 
                 None, self.lower_selection),
            ('RunMenu', None, '_Run'),
            ('RunScript', gtk.STOCK_EXECUTE, None, "F5",None, self.run_script),
            ('DebugScript', None, "Debug Script", "F7",None, self.debug_script),
            ('DebugStep', None, "Step", "F8",None, self.step_script),
            ('DebugNext', None, "Next", "<shift>F7",None, self.next_script),
            ('DebugContinue', None, "Continue", "<control>F7", None, self.continue_script),
            ]
        self.ag = gtk.ActionGroup('edit')
        self.ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(self.ag, 0)
        self.ui.add_ui_from_string(ui_string)
        self.get_parent_window().add_accel_group(self.ui.get_accel_group())
        return (self.ui.get_widget('/menubar'), self.ui.get_widget('/toolbar'))
    
    def set_title(self, title):
        if title is not None:
            self.cb.mainwindow.set_title(title)

    def move_cursor(self, tv, step, count, extend_selection):
        self.update_cursor_position(tv.get_buffer(), tv)

    def update_cursor_position(self, buff, view):
        it = buff.get_iter_at_mark(buff.get_insert())
        if view.get_overwrite():
            ow = "REPL."
        else:
            ow = "INS."
        self.statusbar.push(0, "%s, %s %s" % (it.get_line()+1, 
                it.get_line_offset()+1, ow))
        if not buff.get_modified():
            title = "PIDA " + self.get_current()[0] + "*"
            self.cb.mainwindow.set_title(title)

    def get_parent_window(self):
        return self.cb.mainwindow

    def refresh_browser(self, item):
        name, buff, text, model = self.get_current()
        buff.place_cursor(buff.get_start_iter())
        model = self.listclasses(fname=name)
        self.treeClass.set_model(model)
        self.treeClass.expand_all()
        self.wins[name] = buff, text, model
        pass
    
    def tree_right_clicked(self, tree, event):
        if event.button == 3:
            self.browser_menu.show()
            self.browser_menu.popup(None, None, None, event.button, event.time)
            return
   
    def switch_page_cb(self, notebook, page, pagenum):
        f, b, text, model  = self.get_current(pagenum)
        if not f is None and not b is None:
            if b.get_data("save"):
                model = self.listclasses(fname = f)
            self.set_title(f)

    def get_current(self, page = None):
        if len(self.wins) > 0:
            if page is None:
                page = self.notebook.get_current_page()
            child = self.notebook.get_nth_page(page)
            if not child is None:
                name = self.notebook.get_tab_label_text(child)
                if self.wins.has_key(name):
                    buff, text, model = self.wins[name]
                    return name, buff, text, model
            
        return None, None, None, None

    def _new_tab(self, f, buff = None):
        p = -1
        if not self.wins.has_key(f):
            lm = gtksourceview.SourceLanguagesManager()
            if buff is None:
                buff = gtksourceview.SourceBuffer()
            buff.set_data('languages-manager', lm)
            text = gtksourceview.SourceView(buff)
            font_desc = pango.FontDescription('monospace 10')
            if font_desc:
                text.modify_font(font_desc)
            #~ buffer.connect('mark_set', self.move_cursor_cb, text)
            buff.connect('changed', self.update_cursor_position, text)
            buff.connect('insert-text', self.insert_at_cursor_cb)
            #~ buffer.connect('delete-range', self.delete_range_cb)
            buff.set_data("save", False)
            scrolledwin2 = gtk.ScrolledWindow()
            scrolledwin2.add(text)
            text.set_auto_indent(True)
            text.set_show_line_numbers(True)
            text.set_show_line_markers(True)
            text.set_tabs_width(4)
            text.connect('key-press-event', self.text_key_press_event_cb)
            text.connect('move-cursor', self.move_cursor)
            #text.connect('key-release-event', self.text_key_press_event_cb)
            #text.set_insert_spaces_instead_of_tabs(True)
            text.set_margin(80)
            text.set_show_margin(True)
            text.set_smart_home_end(True)
            text.set_highlight_current_line(True)
            #~ text.connect("grab-focus", self.grab_focus_cb)
            #~ text.connect('delete-from-cursor', self.delete_from_cursor_cb)
            
            text.show()
            l = gtk.Label(f)
            self.notebook.append_page(scrolledwin2, l)
            scrolledwin2.show()
            text.grab_focus()
            self.wins[f] = (buff, text, None)
            scrolledwin2.set_data('filename', f)
            p = len(self.wins) - 1
            self.notebook.set_current_page(-1)
        else:
            for i in range(self.notebook.get_n_pages()):
                if self.notebook.get_nth_page(i).get_data('filename') == f:
                    self.notebook.set_current_page(i)
                    break
        return p

    def insert_at_cursor_cb(self, buff, iter, text, length):
        complete = ""
        name, a,b,c = self.get_current()
        if self.ac_w is not None:
            self.ac_w.hide()
        if text in special_chars:
            name, buff, text, model = self.get_current()
            iter2 = buff.get_iter_at_mark(buff.get_insert())
            complete = self.get_context(buff, iter2)
            if complete.isdigit():
                # to avoid problems with float point.
                return
        if len(complete.strip()) > 0:
            lst = importsTipper.GenerateTip(complete, os.path.dirname(name))
            if self.ac_w is None:
                self.ac_w = AutoCompletionWindow(text, iter2, complete, 
                                                lst, self.cb.mainwindow)
            else:
                self.ac_w.set_list(text, iter2, complete, 
                                   lst, self.cb.mainwindow)
        return
        
    def get_context(self, buff, iter):
        iter2 = iter.copy()
        iter.backward_word_starts(1)
        iter3 = iter.copy()
        iter3.backward_chars(1)
        prev = iter3.get_text(iter)
        complete = iter.get_text(iter2)
        if prev in (".", "_"):
            t = self.get_context(buff, iter)
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
        try:
            fd = open(fname)
            self._new_tab(fname)
            buff, text, model = self.wins[fname]
            buff.set_text('')
            buf = fd.read(BLOCK_SIZE)
            while buf != '':
                buff.insert_at_cursor(buf)
                buf = fd.read(BLOCK_SIZE)
            text.queue_draw()
            self.set_title(os.path.basename(fname))
            self.dirname = os.path.dirname(fname)
            buff.set_modified(False)
            self.new = 0
        except:
            dlg = gtk.MessageDialog(self.get_parent_window(),
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                    "Can't open " + fname)
            print sys.exc_info()[1]
            resp = dlg.run()
            dlg.hide()
            return
        self.check_mime(fname)
        text.grab_focus()

    def check_mime(self, fname):
        buff, text, model = self.wins[fname]
        manager = buff.get_data('languages-manager')
        if os.path.isabs(fname):
            path = fname
        else:
            path = os.path.abspath(fname)
        uri = gnomevfs.URI(path)
        mime_type = gnomevfs.get_mime_type(path) # needs ASCII filename, not URI
        pagenum = self.notebook.get_current_page()
        self.filetypes[pagenum] = 'None'
        if mime_type:
            language = manager.get_language_from_mime_type(mime_type)
            if language:
                buff.set_highlight(True)
                buff.set_language(language)
                self.filetypes[pagenum] = language.get_name().lower()
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
        buff.set_data("save", False)

    def chk_save(self):
        fname, buff, text, model = self.get_current()
        if buff is None:
            return False
        if buff.get_modified():
            dlg = gtk.Dialog('Unsaved File', self.get_parent_window(),
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_YES, gtk.RESPONSE_YES,
                          gtk.STOCK_NO, gtk.RESPONSE_NO,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            lbl = gtk.Label((fname or "Untitled")+
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
        if self.chk_save(): return

        global newnumber
        self._new_tab("untitled%s.py" % newnumber)
        newnumber += 1
        fname, buff, text, model = self.get_current()
        buff.set_text("")
        buff.set_modified(False)
        self.new = 1
        manager = buff.get_data('languages-manager')
        language = manager.get_language_from_mime_type("text/x-python")
        buff.set_highlight(True)
        buff.set_language(language)

        return

    def file_open(self, mi=None):

        fname = dialogs.OpenFile('Open File', self.get_parent_window(),
                                  None, None, "*.py")
        if not fname: return
        self.load_file(fname)
        self.cb.mainwindow.set_title("PIDA " + fname)
        return

    def file_save(self, mi=None, fname=None):
        if self.new:
            return self.file_saveas()

        f, buff, text, model = self.get_current()
        curr_mark = buff.get_iter_at_mark(buff.get_insert())

        ret = False

        if fname is None:
            fname = f

        try:

            start, end = buff.get_bounds()
            blockend = start.copy()
            fd = open(fname, "w")

            while blockend.forward_chars(BLOCK_SIZE):
                buf = buff.get_text(start, blockend)
                fd.write(buf)
                start = blockend.copy()

            buf = buff.get_text(start, blockend)
            fd.write(buf)
            fd.close()
            buff.set_modified(False)
            buff.set_data("save", True)
            self.cb.mainwindow.set_title("PIDA " + fname)
            ret = True

            del self.wins[f]
            self.wins[fname] = buff, text, model
            page = self.notebook.get_current_page()
            self.notebook.set_tab_label_text(self.notebook.get_nth_page(page), fname)
            

        except:
            dlg = gtk.MessageDialog(self.get_parent_window(),
                                gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                "Error saving file " + fname)
            print sys.exc_info()[1]
            resp = dlg.run()
            dlg.hide()

        self.check_mime(fname)
        buff.place_cursor(curr_mark)
        text.grab_focus()

        return ret

    def file_saveas(self, mi=None):
        f, buffer, text, model = self.get_current()
        f = dialogs.SaveFile('Save File As', self.get_parent_window(), self.dirname,
                                  f)
        if not f: return False

        self.dirname = os.path.dirname(f)
        self.set_title(os.path.basename(f))
        self.new = 0
        return self.file_save(fname=f)

    def file_close(self, mi=None, event=None):
        page = self.notebook.get_current_page()
        child = self.notebook.get_nth_page(page)
        f=self.notebook.get_tab_label_text(child)
        del self.wins[f]
        self.notebook.remove(child)
        self.cb.edit('getbufferlist')

        return

    def file_exit(self, mi=None, event=None):
        if self.chk_save(): return True
        self.hide()
        self.destroy()
        if self.quit_cb: self.quit_cb(self)
        return False

    def edit_cut(self, mi):
        buff = self.get_current()[1]
        buff.cut_clipboard(self.clipboard, True)
        return

    def edit_copy(self, mi):
        buff = self.get_current()[1]
        buff.copy_clipboard(self.clipboard)
        return

    def edit_paste(self, mi):
        buff = self.get_current()[1]
        buff.paste_clipboard(self.clipboard, None, True)
        return

    def edit_clear(self, mi):
        buff = self.get_current()[1]
        buff.delete_selection(True, True)
        return

    def edit_find(self, mi): 
        def dialog_response_callback(dialog, response_id):
            if response_id == gtk.RESPONSE_CLOSE:
                dialog.destroy()
                return
            self._search(search_text.get_text(), self.last_search_iter)
        buff = self.get_current()[1]
        search_text = gtk.Entry()
        s = buff.get_selection_bounds()
        if len(s) > 0:
            search_text.set_text(buff.get_slice(s[0], s[1]))
        dialog = gtk.Dialog("Search", self.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_FIND, RESPONSE_FORWARD,
                             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        dialog.vbox.pack_end(search_text, True, True, 0)
        dialog.connect("response", dialog_response_callback)
        dialog.set_default_response(RESPONSE_FORWARD)
        search_text.set_activates_default(True)
        search_text.show()
        search_text.grab_focus()
        dialog.show_all()
        response_id = dialog.run()
        
    def edit_replace(self, mi): 
        def dialog_response_callback(dialog, response_id):
            if response_id == gtk.RESPONSE_CLOSE:
                dialog.destroy()
                return
            if response_id == RESPONSE_FORWARD:
                self._search(search_text.get_text(), self.last_search_iter)
                return
            if response_id == RESPONSE_REPLACE:
                self._search(search_text.get_text(), self.last_search_iter)
                start, end = buff.get_selection_bounds()
                buff.delete(start, end)
                buff.insert(start, replace_text.get_text())
                self.last_search_iter = buff.get_iter_at_mark(buff.get_insert())
                start = buff.get_iter_at_mark(buff.get_insert())
                start.backward_chars(len(replace_text.get_text()))
                buff.select_range(start, self.last_search_iter)
                return
                
        buff = self.get_current()[1]
        search_text = gtk.Entry()
        replace_text = gtk.Entry() 
        s = buff.get_selection_bounds()
        if len(s) > 0:
            search_text.set_text(buff.get_slice(s[0], s[1]))
        dialog = gtk.Dialog("Search", self.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_FIND, RESPONSE_FORWARD,
                             gtk.STOCK_FIND_AND_REPLACE, RESPONSE_REPLACE,
                             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        lbl = gtk.Label("Find what:")
        dialog.vbox.pack_start(lbl, True, True, 0)
        dialog.vbox.pack_start(search_text, True, True, 0)
        lbl = gtk.Label("Replace with:")
        dialog.vbox.pack_start(lbl, True, True, 0)
        dialog.vbox.pack_start(replace_text, True, True, 0)
        dialog.connect("response", dialog_response_callback)
        dialog.set_default_response(RESPONSE_FORWARD)
        search_text.set_activates_default(True)
        replace_text.set_activates_default(True)
        search_text.show()
        replace_text.show()
        search_text.grab_focus()
        dialog.show_all()
        response_id = dialog.run()
    
    def _search(self, search_string, iter = None):
        f, buff, text, model = self.get_current()
        if iter is None:
            start = buff.get_start_iter()
        else:
            start = iter
        i = 0
        if search_string:
            self.search_string = search_string
            res = start.forward_search(search_string, gtk.TEXT_SEARCH_TEXT_ONLY)
            if res:
                match_start, match_end = res
                buff.place_cursor(match_start)
                buff.select_range(match_start, match_end)
                text.scroll_to_iter(match_start, 0.25)
                self.last_search_iter = match_end
            else:
                self.search_string = None
                self.last_search_iter = buff.get_iter_at_mark(buff.get_insert())
            
    def edit_find_next(self, mi):
        self._search(self.search_string, self.last_search_iter)
    
    def goto_line(self, mi=None):
        def dialog_response_callback(dialog, response_id):
            if response_id == gtk.RESPONSE_CLOSE:
                dialog.destroy()
                return
            line = line_text.get_text()
            if line.isdigit():
                f, buff, tv, model = self.get_current()
                titer = buff.get_iter_at_line(int(line)-1)
                tv.scroll_to_iter(titer, 0.25)
                buff.place_cursor(titer)
                tv.grab_focus()
                dialog.destroy()
       
        line_text = gtk.Entry()
        dialog = gtk.Dialog("Goto Line", self.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_GO_FORWARD, RESPONSE_FORWARD,
                             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        dialog.vbox.pack_end(line_text, True, True, 0)
        dialog.connect("response", dialog_response_callback)
        dialog.set_default_response(RESPONSE_FORWARD)
        line_text.set_activates_default(True)
        line_text.show()
        line_text.grab_focus()
        dialog.show_all()
        response_id = dialog.run()

    def comment_block(self, mi=None):
        comment = "#"
        buf = self.get_current()[1]
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
        buf = self.get_current()[1]
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
        buf = self.get_current()[1]
        it = buf.get_iter_at_mark(buf.get_insert())
        line = it.get_line()
        start = buf.get_iter_at_line(line)
        end = buf.get_iter_at_line(line+1)
        if start.get_line() == end.get_line():
            end.forward_to_end()
        buf.delete(start, end)
            
    def duplicate_line(self, mi):
        buf = self.get_current()[1]
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
        buf = self.get_current()[1]
        bound = buf.get_selection_bounds()
        if not len(bound) == 0:
            start, end = bound
            text = buf.get_text(start, end)
            buf.delete(start, end)
            buf.insert(start, text.upper())
            
    def lower_selection(self, mi):
        buf = self.get_current()[1]
        bound = buf.get_selection_bounds()
        if not len(bound) == 0:
            start, end = bound
            text = buf.get_text(start, end)
            buf.delete(start, end)
            buf.insert(start, text.lower())
    
    def run_script(self, mi):
        self.plugin.do_evt("bufferexecute") 
        
    def debug_script(self, mi):
        self.plugin.do_evt('debuggerload')
        buff = self.get_current()[1]
        tv = self.get_current()[2]
        titer = buff.get_iter_at_line(0)
        tv.scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)
        
    def step_script(self, mi):
        self.plugin.do_evt('step')
        buff = self.get_current()[1]
        tv = self.get_current()[2]
        line = self.plugin.current_frame.lineno
        titer = buff.get_iter_at_line(int(line)-1)
        tv.scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)

    def next_script(self, mi):
        self.plugin.do_evt('next')
        line = self.plugin.current_frame.lineno
        buff = self.get_current()[1]
        tv = self.get_current()[2]
        titer = buff.get_iter_at_line(int(line)-1)
        tv.scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)

    def continue_script(self, mi):
        self.plugin.do_evt('continue')
        line = self.plugin.current_frame.lineno
        buff = self.get_current()[1]
        tv = self.get_current()[2]
        titer = buff.get_iter_at_line(int(line)-1)
        tv.scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)
        
class AutoCompletionWindow(gtk.Window):
    
    def __init__(self,  source_view, trig_iter, text, list, parent):
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_decorated(False)
        self.store = gtk.ListStore(str, str, str)
        self.source = source_view
        self.iter = trig_iter
        frame = gtk.Frame()
        
        for i in list:
            if i[3] == importsTipper.TYPE_UNKNOWN:
                stock = gtk.STOCK_NEW
            else:
                stock = gtk.STOCK_CONVERT
                
            self.store.append((stock, i[0], i[2]))
        self.tree = gtk.TreeView(self.store)
        
        render = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn('', render, stock_id=0)
        self.tree.append_column(column)
        col = gtk.TreeViewColumn()
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn('', render, text=1)
        self.tree.append_column(column)
        col = gtk.TreeViewColumn()
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn('', render, text=2)
        self.tree.append_column(column)
        rect = source_view.get_iter_location(trig_iter)
        wx, wy = source_view.buffer_to_window_coords(gtk.TEXT_WINDOW_WIDGET, 
                                rect.x, rect.y + rect.height)

        tx, ty = source_view.get_window(gtk.TEXT_WINDOW_WIDGET).get_origin()
        wth, hht = parent.get_size()
        width = wth - (tx+wx)
        height = hht - (ty+wy)
        if width > 200: width = 200
        if height > 200: height = 200
        self.move(wx+tx, wy+ty)
        self.add(frame)
        frame.add(self.tree)
        self.tree.set_size_request(width, height)
        self.tree.connect('row-activated', self.row_activated_cb)
        self.tree.connect('focus-out-event', self.focus_out_event_cb)
        self.tree.connect('key-press-event', self.key_press_event_cb)
        self.tree.set_search_column(1)
        self.tree.set_search_equal_func(self.search_func)
        self.tree.set_headers_visible(False)
        self.set_transient_for(parent)
        self.show_all()
        self.tree.grab_focus()
        
    def set_list(self, source_view, trig_iter, text, list, parent):
        self.store = gtk.ListStore(str, str, str)
        self.source = source_view
        self.iter = trig_iter
        for i in list:
            if i[3] == importsTipper.TYPE_UNKNOWN:
                stock = gtk.STOCK_NEW
            else:
                stock = gtk.STOCK_CONVERT
            self.store.append((stock, i[0], i[2]))
        self.tree.set_model(self.store)
        self.tree.set_search_column(1)
        self.tree.set_search_equal_func(self.search_func)
        rect = source_view.get_iter_location(trig_iter)
        wx, wy = source_view.buffer_to_window_coords(gtk.TEXT_WINDOW_WIDGET, 
                                rect.x, rect.y + rect.height)
        tx, ty = source_view.get_window(gtk.TEXT_WINDOW_WIDGET).get_origin()
        wth, hht = parent.get_size()
        print wth, hht 
        wth += tx
        hht += ty
        width = wth - (wx+tx) 
        height = hht - (wy+ty)
        if width > 200: width = 200
        if height > 200: height = 200
        print wy+ty
        print width, height
        self.move(wx+tx, wy+ty)
        self.tree.set_size_request(width, height)
        self.show_all()
        self.tree.grab_focus()
        
    def row_activated_cb(self, tree, path, view_column, data = None):
        complete = self.store[path][1] + self.store[path][2]
        buff = self.source.get_buffer()
        buff.insert_at_cursor(complete)
        self.hide()
        
    def focus_out_event_cb(self, widget, event):
        self.hide()

    def key_press_event_cb(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.hide()
            
    def search_func(self, model, column, key, iter):
        return not model.get_value(iter, column).startswith(key)
        


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

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        fname = sys.argv[-1]
    else:
        fname = ""
    edit(fname, mainwin=True)

