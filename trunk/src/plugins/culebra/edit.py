#!/usr/bin/env python

# This is based on pygtk2 examples and idle

#import pygtk
#pygtk.require('2.0')
import gtk
import sys, os
import pango
import dialogs
import gtksourceview
import gnomevfs

BLOCK_SIZE = 2048

special_chars = (" ", "\n", ".", ":", ",", "'", 
                '"', "(", ")", "{", "}", "[", "]")
RESPONSE_FORWARD = 0
RESPONSE_BACKWARD = 1

class EditWindow(gtk.EventBox):

    def __init__(self, cb, quit_cb=None):
        self.cb = cb
        #gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        gtk.EventBox.__init__(self)
        self.search_string = None
        self.last_search_iter = None
        self.completion_win = None
        self.insert_string = None
        self.cursor_iter = None
        self.wins = {}
        self.current_word = ""
        self.wl = []

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

        self.scrolledwin2 = gtk.ScrolledWindow()
        self.scrolledwin2.show()
        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(True)
        self.notebook.set_scrollable(True)
        self.hpaned.add2(self.notebook)
        self.hpaned.set_position(200)

        self.notebook.show()
        self.notebook.connect('switch-page', self.switch_page_cb)        
        
        self.dirty = 0
        self.file_new()

        self.clipboard = gtk.Clipboard(selection='CLIPBOARD')
        self.dirname = "."

        self.browser_menu = gtk.Menu()
        refresh_item = gtk.MenuItem("Refresh")
        self.browser_menu.append(refresh_item)
        refresh_item.show()
        refresh_item.connect("activate", self.refresh_browser)
        return
    
    def get_parent_window(self):
        return self.cb.mainwindow

    def refresh_browser(self, item):
        name, buffer, text, model = self.get_current()
        
        buffer.place_cursor(buffer.get_start_iter())
        model = self.listclasses(fname=name)
        self.treeClass.set_model(model)
        self.treeClass.expand_all()
        self.wins[name] = buffer, text, model
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
            
            #~ print page, child

            if not child is None:
                name = self.notebook.get_tab_label_text(child)
                #~ print name
                
                if self.wins.has_key(name):
                    buffer, text, model = self.wins[name]
                    return name, buffer, text, model
            
        return None, None, None, None

    def _new_tab(self, f, buffer = None):

        p = -1

        if not self.wins.has_key(f):

            lm = gtksourceview.SourceLanguagesManager()

            if buffer is None:
                buffer = gtksourceview.SourceBuffer()

            buffer.set_data('languages-manager', lm)
            text = gtksourceview.SourceView(buffer)
            font_desc = pango.FontDescription('monospace 10')

            if font_desc:
                text.modify_font(font_desc)

            #~ buffer.connect('mark_set', self.move_cursor_cb, text)
            #~ buffer.connect('changed', self.update_cursor_position, text)
            #~ buffer.connect('insert-text', self.insert_at_cursor_cb)
            #~ buffer.connect('delete-range', self.delete_range_cb)
            buffer.set_data("save", False)

            scrolledwin2 = gtk.ScrolledWindow()

            scrolledwin2.add(text)

            text.set_auto_indent(True)
            text.set_show_line_numbers(True)
            #~ text.set_show_line_markers(True)
            #text.set_tabs_width(4)
            #~ text.connect("grab-focus", self.grab_focus_cb)
            #~ text.connect('delete-from-cursor', self.delete_from_cursor_cb)
            text.show()

            l = gtk.Label(f)
            
            self.notebook.append_page(scrolledwin2, l)

            scrolledwin2.show()
            text.grab_focus()
            self.wins[f] = (buffer, text, None)
            #~ print f, self.wins[f]


        p = len(self.wins) - 1

        self.notebook.set_current_page(-1)

        return p

    def move_cursor_cb (self, buffer, cursoriter, mark, view):
        self.update_cursor_position(buffer, view)

    def update_cursor_position(self, buffer, view):

        name, buff, text, model = self.get_current()
        
        if text is None:
            return
            
        tabwidth = text.get_tabs_width()

        iter = buffer.get_iter_at_mark(buffer.get_insert())
        nchars = iter.get_offset()

        row = iter.get_line() + 1

        start = iter
        start.set_line_offset(0)
        col = 0


        while not start.equal(iter):
            if start.get_char == '\t':
                col += (tabwidth - (col % tabwidth))
            else:
                col += 1
                start = start.forward_char()
        
    def console_move_cursor_cb(self, buffer, cursoriter, mark, view=None):
        
        s = buffer.get_iter_at_line(cursoriter.get_line())
        e = cursoriter.copy()
        
        e.forward_to_line_end()
        
        line = buffer.get_text(s, e)
        
        if "line" in line:
            lsplit = line.split(",")
            
            f = lsplit[0]
            l = lsplit[1]
            
            lineno = l.strip().split(" ")[1]
            file = f.strip().split(" ")[1].replace('"', "")
            
            if not self.wins.has_key(file):
                self.load_file(file)
                
            pages = self.notebook.get_n_pages()
            n = 0
            child = self.notebook.get_nth_page(n)
            
            while self.notebook.get_tab_label_text(child) != file and n < pages:
                    n += 1
                    child = self.notebook.get_nth_page(n)
                    
            self.notebook.set_current_page(n)
            
            b, t, m = self.wins[file]
            iter = b.get_iter_at_line(int(lineno)-1)

            t.scroll_to_iter(iter, 0.0)
            b.place_cursor(iter)
            t.grab_focus()

        len

    def insert_at_cursor_cb(self, textbuffer, iter, text, length):
        
        return 
        if text in special_chars:
            self.current_word = ""
        else:
            self.current_word += text
        
        if len(text) == 1: 
            if ord(text) == 9: self.current_word = ""
        
        name, buff, t_v, model = self.get_current()

        
        if len(self.wl):
            w = AutoCompletionWindow(self.wl, t_v, iter)
        return

    def load_file(self, fname):


        try:
            fd = open(fname)

            self._new_tab(fname)

            buffer, text, model = self.wins[fname]

            buffer.set_text('')
            buf = fd.read(BLOCK_SIZE)

            while buf != '':
                buffer.insert_at_cursor(buf)
                buf = fd.read(BLOCK_SIZE)

            text.queue_draw()
            self.set_title(os.path.basename(fname))

            self.dirname = os.path.dirname(fname)
            buffer.set_modified(False)
            self.new = 0
            
        except:
            print sys.exc_info()[1]
            dlg = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                    "Can't open " + fname)
            resp = dlg.run()
            dlg.hide()
            return

        #~ print "check mime"
        self.check_mime(fname)

    def check_mime(self, fname):

        buffer, text, model = self.wins[fname]

        manager = buffer.get_data('languages-manager')

        if os.path.isabs(fname):
            path = fname
        else:
            path = os.path.abspath(fname)

        uri = gnomevfs.URI(path)

        mime_type = gnomevfs.get_mime_type(path) # needs ASCII filename, not URI

        if mime_type:
            language = manager.get_language_from_mime_type(mime_type)
            if language:
                buffer.set_highlight(True)
                buffer.set_language(language)
            else:
                print 'No language found for mime type "%s"' % mime_type
                buffer.set_highlight(False)
        else:
            print 'Couldn\'t get mime type for file "%s"' % fname
            buffer.set_highlight(False)

        buffer.place_cursor(buffer.get_start_iter())
        buffer.set_data("save", False)

    def view_console(self, action):
        #~ print "console ", param
        pass

    def clear_console(self, action):
        
        self.console.buffer.set_text('')

    def run_script(self, action):

        fname, buffer, text, model = self.get_current()

        #~ print "running ", fname

        if not fname or not os.path.exists(fname):
            dlg = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                "Invalid filename "+fname)
            dlg.run()
            return

        args = ""

        self.file_save(fname)
        fname, buffer, text, model = self.get_current()


        #self.console.buffer.disconnect(self.console_hid)
        out = self.console.run("execfile('%s')" % fname)
        self.console_hid = self.console.buffer.connect('mark_set', self.console_move_cursor_cb)
        #traceback.print_stack(file=out)
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
                </menu>
                <menu name='View' action='View'>
                        <menuitem action='ViewConsole'/>
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
            ('EditFindNext', None, 'Find _Next', None, None,
             self.edit_find_next),
            ('View', None, "_View"),
            ('ViewConsole', None, '_View Console', None, None, self.view_console),
            ]
        self.ag = gtk.ActionGroup('edit')
        self.ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(self.ag, 0)
        self.ui.add_ui_from_string(ui_string)
        self.get_parent_window().add_accel_group(self.ui.get_accel_group())
        return (self.ui.get_widget('/menubar'), self.ui.get_widget('/toolbar'))

    def chk_save(self):

        fname, buffer, text, model = self.get_current()

        if buffer is None:
            return 0

        if buffer.get_modified():
            dlg = gtk.Dialog('Unsaved File', self,
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
                return 0
            if ret == gtk.RESPONSE_YES:
                if self.file_save():
                    return 0
            return 1
        return 0

    def file_new(self, mi=None):
        if self.chk_save(): return

        self._new_tab("untitled.py")

        fname, buffer, text, model = self.get_current()

        buffer.set_text("")
        buffer.set_modified(False)

        #self.set_title(fname)
        self.new = 1
        manager = buffer.get_data('languages-manager')
        language = manager.get_language_from_mime_type("text/x-python")
        buffer.set_highlight(True)
        buffer.set_language(language)

        return

    def file_open(self, mi=None):

        fname = dialogs.OpenFile('Open File', self, None, None, "*")
        if not fname: return
        self.load_file(fname)
        return

    def file_save(self, mi=None, fname=None):
        if self.new:
            return self.file_saveas()

        f, buffer, text, model = self.get_current()

        ret = False

        if fname is None:
            fname = f

        try:

            start, end = buffer.get_bounds()
            blockend = start.copy()
            fd = open(fname, "w")

            while blockend.forward_chars(BLOCK_SIZE):
                buf = buffer.get_text(start, blockend)
                fd.write(buf)
                start = blockend.copy()

            buf = buffer.get_text(start, blockend)
            fd.write(buf)
            fd.close()
            buffer.set_modified(False)
            buffer.set_data("save", True)
            ret = True

            del self.wins[f]
            self.wins[fname] = buffer, text, model
            page = self.notebook.get_current_page()
            self.notebook.set_tab_label_text(self.notebook.get_nth_page(page), fname)

        except:
            dlg = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                "Error saving file " + fname)
            resp = dlg.run()
            dlg.hide()

        self.check_mime(fname)

        return ret

    def file_saveas(self, mi=None):
        f, buffer, text, model = self.get_current()
        f = dialogs.SaveFile('Save File As', self, self.dirname,
                                  fname)
        if not f: return False

        self.dirname = os.path.dirname(f)
        self.set_title(os.path.basename(f))
        self.new = 0
        return self.file_save(fname=f)

    def file_close(self, mi=None, event=None):

        page = self.notebook.get_current_page()
        child = self.notebook.get_nth_page(page)
        
        #~ print child
        f=self.notebook.get_tab_label_text(child)
        #~ print f
        
        #~ print "cerrando ", f

        del self.wins[f]
        self.notebook.remove(child)

        return

    def file_exit(self, mi=None, event=None):
        if self.chk_save(): return True
        self.hide()
        self.destroy()
        if self.quit_cb: self.quit_cb(self)
        return False

    def edit_cut(self, mi):
        fname, buffer, text, model = self.get_current()
        buffer.cut_clipboard(self.clipboard, True)
        return

    def edit_copy(self, mi):
        fname, buffer, text, model = self.get_current()
        buffer.copy_clipboard(self.clipboard)
        return

    def edit_paste(self, mi):
        fname, buffer, text, model = self.get_current()
        buffer.paste_clipboard(self.clipboard, None, True)
        return

    def edit_clear(self, mi):
        fname, buffer, text, model = self.get_current()
        buffer.delete_selection(True, True)
        return

    def edit_find(self, mi): 
        def dialog_response_callback(dialog, response_id):
            if response_id == gtk.RESPONSE_CLOSE:
                dialog.destroy()
                return
            self._search(search_text.get_text(), self.last_search_iter)
        f, buffer, text, model = self.get_current()
        search_text = gtk.Entry()
        s = buffer.get_selection_bounds()
        if len(s) > 0:
            search_text.set_text(buffer.get_slice(s[0], s[1]))
        dialog = gtk.Dialog("Search", self,
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_FIND, RESPONSE_FORWARD,
                             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        dialog.vbox.pack_end(search_text, True, True, 0)
        dialog.connect("response", dialog_response_callback)
        search_text.show()
        search_text.grab_focus()
        dialog.show_all()
        response_id = dialog.run()
    
    def _search(self, search_string, iter = None):
        f, buffer, text, model = self.get_current()
        if iter is None:
            start = buffer.get_start_iter()
        else:
            start = iter
        i = 0
        if search_string:
            self.search_string = search_string
            res = start.forward_search(search_string, gtk.TEXT_SEARCH_TEXT_ONLY)
            if res:
                match_start, match_end = res
                buffer.place_cursor(match_start)
                buffer.select_range(match_start, match_end)
                text.scroll_to_iter(match_start, 0.0)
                self.last_search_iter = match_end
                #~ print res
            else:
                self.search_string = None
                self.last_search_iter = None
    
    def edit_find_next(self, mi):
        self._search(self.search_string, self.last_search_iter)
        
def edit(fname, mainwin=False):
    if mainwin: quit_cb = lambda w: gtk.main_quit()
    else:       quit_cb = None
    w = EditWindow(quit_cb=quit_cb)
    if fname != "":
        w.file_new()
    w.maximize()
    w.show()
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

