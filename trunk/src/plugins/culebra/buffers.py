import gtk
import gtksourceview
import gobject
import keyword

import components as binding
from events import EventsDispatcher
import keyword
import importsTipper
import os

def search_iterator (text_buffer, search_text, find_forward = True, start_in_cursor = True):
    """
    This function implements an iterator for searching a gtk.TextBuffer for
    a certain string.
    
    It supports forward and backwards search.
    
    It also supports finding from the start or from where the cursor is located.
    """

    if start_in_cursor:
        bounds = text_buffer.get_selection_bounds ()
        if len (bounds) == 0:
            text_iter = text_buffer.get_iter_at_mark(text_buffer.get_insert())
        else:
            text_iter = find_forward and bounds[1] or bounds[0]
    else:
        if find_forward:
            text_iter = text_buffer.get_start_iter()
        else:
            text_iter = text_buffer.get_end_iter()
    
    first_iter = None
    bounds = 1
    while bounds is not None:
        if find_forward:
            search = text_iter.forward_search
            
        else:
            search = text_iter.backward_search
            
        bounds = search (search_text, gtk.TEXT_SEARCH_TEXT_ONLY, limit = None)
        
        if bounds is None:
            break
            
        yield bounds
        
        if find_forward:
            text_iter = bounds[1]
        else:
            text_iter = bounds[0]


class AutoCompletionWindow(gtk.Window):
    
    def __init__(self,  source_view, trig_iter, text, lst, parent, mod, cbound):
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_decorated(False)
        self.store = gtk.ListStore(str, str, str)
        self.source = source_view
        self.it = trig_iter
        self.mod = mod
        self.cbounds = cbound
        self.found = False
        self.text = text
        frame = gtk.Frame()
        
        for i in lst:
            self.store.append((gtk.STOCK_CONVERT, i, ""))
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
        self.tree.set_cursor((0,))
        self.tree.grab_focus()
        
    def row_activated_cb(self, tree, path, view_column, data = None):
        self.complete = self.store[path][1] + self.store[path][2]
        self.insert_complete()
        
    def insert_complete(self):
        buff = self.source.get_buffer()
        try:
            if not self.mod:
                s, e = self.cbounds
                buff.select_range(buff.get_iter_at_mark(s), buff.get_iter_at_mark(e))
                start, end = buff.get_selection_bounds()
                buff.delete(start, end)
                buff.insert(start, self.complete)
            else:
                buff.insert_at_cursor(self.complete)
        except:
            buff.insert_at_cursor(self.complete[len(self.text):])
        self.hide()

    def focus_out_event_cb(self, widget, event):
        self.hide()

    def key_press_event_cb(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.hide()
        elif event.keyval == gtk.keysyms.BackSpace:
            self.hide()
            
    def search_func(self, model, column, key, it):
        
        if self.mod:
            cp_text = key
        else:
            cp_text = self.text + key
        self.complete = cp_text
        
        if model.get_path(model.get_iter_first()) == model.get_path(it):
            self.found = False
        if model.get_value(it, column).startswith(cp_text):
            self.found = True
        if model.iter_next(it) is None and not self.found:
            if self.text != "" and model.get_value(it, column).startswith(self.complete):
                self.complete = model.get_value(it, 1)
            elif not model.get_value(it, column).startswith(self.complete):
                pass
            else:
                self.complete = key
            self.insert_complete()
            self.hide()
        return not model.get_value(it, column).startswith(cp_text)

#################
# gtk.TextBuffer utility functions
def get_buffer_selection (buffer):
    """Returns the selected text, when nothing is selected it returns the empty
    string."""
    bounds = buffer.get_selection_bounds()
    if len(bounds) == 0:
        return ""
    else:
        return buffer.get_slice(*bounds)

class SearchMethod (binding.Component, object):
    buffer = binding.Obtain ("..")
    can_find_forward = False
    can_find_backwards = False
    
    __search_text = ""

    def get_search_text (self):
        return self.__search_text
    
    def set_search_text (self, search_text):
        has_changed = self.__search_text != search_text
        self.__search_text = search_text
        
        if has_changed:    
            self._on_changed (search_text)
            
    search_text = property (get_search_text, set_search_text)
        
    def search_tag (self):
        return self.buffer.create_tag(
            "search_markers",
            background="yellow",
            foreground="black",
        )
    
    search_tag = binding.Make (search_tag)
    
    def events (self):
        events = EventsDispatcher ()
        self._no_more_entries = events.create_event ("no-more-entries")
        self._on_changed = events.create_event ("changed")
        events.register ("changed", self.on_search_changed)
        return events
    
    events = binding.Make (events, uponAssembly = True)
    
    changed_source = None

    is_enabled = property (lambda self: self.changed_source is not None)

    # Methods
    def on_changed (self, *args):
        # TODO: optimize this
        self.highlight_string (self.search_text)
        
    def disable (self):
        # Clear old tags
        self.buffer.remove_tag(
            self.search_tag,
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter()
        )
        if self.changed_source is not None:
            gobject.source_remove (self.changed_source)

    def enable (self):
        self.on_changed()

        if self.changed_source is not None:
            return
            
        self.changed_source = self.buffer.connect("changed", self.on_changed)
        
    def highlight_string (self, search_text):
        self.buffer.remove_tag(
            self.search_tag,
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter()
        )
        
        if search_text is None or search_text == "":
            return
        
        # Apply tag to found entries
        bounds = search_iterator (self.buffer, search_text, start_in_cursor = False)
        for start_iter, end_iter in bounds:
            self.buffer.apply_tag (self.search_tag, start_iter, end_iter)
        
    def on_search_changed (self, search_text):
        if not self.is_enabled:
            return
        self.on_changed ()
        
    def __call__(self, scroll=True, editor = None, find_forward = True):
            
        if self.search_text is None or self.search_text == "":
            return False
            
        end_reached = False
        bounds = search_iterator(self.buffer, self.search_text, find_forward = find_forward)
        
        try:
            start_iter, end_iter = bounds.next ()
            self.buffer.place_cursor (start_iter)
            self.buffer.select_range (start_iter, end_iter)
            return True
        
        except StopIteration:
            self._no_more_entries (find_forward)
            return False

class ReplaceMethod (binding.Component):
    buffer = binding.Obtain ("..")
    search = binding.Obtain ("../search")

    def events (self):
        events = EventsDispatcher ()
        self._on_changed = events.create_event ("changed")
        return events
    
    events = binding.Make (events, uponAssembly = True)

    _replace_text = ""
    def get_replace_text (self):
        return self._replace_text
    
    def set_replace_text (self, replace_text):
        has_changed = self._replace_text != replace_text
        self._replace_text = replace_text
        if has_changed:
            self._on_changed (replace_text)
            
    replace_text = property (get_replace_text, set_replace_text)
    
    def __call__ (self):
        if get_buffer_selection (self.buffer) != self.search.search_text:
            return False

        start, end = self.buffer.get_selection_bounds ()
        self.buffer.delete(start, end)
        self.buffer.insert(start, self.replace_text)
        start = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        start.backward_chars(len(self.replace_text))
        
        return True

        
class CulebraBuffer(gtksourceview.SourceBuffer, binding.Component):
    
    search = binding.Make (SearchMethod)
    
    replace = binding.Make (ReplaceMethod)
    
    def __init__(self, filename = None, encoding = "utf-8"):
        gtksourceview.SourceBuffer.__init__(self)
        binding.Component.__init__ (self, None)
        
        lm = gtksourceview.SourceLanguagesManager()
        self.languages_manager = lm
        language = lm.get_language_from_mime_type("text/x-python")
        self.set_highlight(True)
        self.set_language(language)
        self.search_mark = self.create_mark('search', self.get_start_iter())
        
        self.filename = filename
        self.encoding = encoding

    def replace_all (self):
        # move cursor to the start of the buffer
        start_iter = self.get_start_iter ()
        self.place_cursor (start_iter)
        
        # Now search forward
        while self.search():
            # When we find an item replace it
            self.replace()
        
    def get_filename (self):
        if self.__filename is None:
            return "New File"
        return self.__filename
    
    def set_filename (self, filename):
        self.__filename = filename
    
    filename = property (get_filename, set_filename)
    
    def get_encoding (self):
        return self.__encoding
    
    def set_encoding (self, encoding):
        self.__encoding = encoding
    
    encoding = property (get_encoding, set_encoding)
    
    def get_is_new (self):
        return self.__filename is None
    
    is_new = property (get_is_new)
    
    
    def get_context(self, it, sp=False):
        iter2 = it.copy()
        if sp:
            it.backward_word_start()
        else:
            it.backward_word_starts(1)
        iter3 = it.copy()
        iter3.backward_chars(1)
        prev = iter3.get_text(it)
        complete = it.get_text(iter2)
        self.context_bounds = (self.create_mark('cstart',it), self.create_mark('cend',iter2))
        if prev in (".", "_"):
            t = self.get_context(it)
            return t + complete
        else:
            count = 0
            return complete
            
            
    def show_completion(self, text, it, editor, mw):
        complete = ""
        iter2 = self.get_iter_at_mark(self.get_insert())
        s, e = self.get_bounds()
        text_code = self.get_text(s, e)
        lst_ = []

        mod = False
        if text != '.':
            complete = self.get_context(iter2, True)
            if "\n" in complete or complete.isdigit() or complete.isspace():
                return
            else:
                complete = complete + text
            try:
                c = compile(text_code, '<string>', 'exec')
                lst_ = [a for a in c.co_names if a.startswith(complete)]
                con = map(str, c.co_consts)
                con = [a for a in con if a.startswith(complete) and a not in lst_]
                lst_ += con
                lst_ += keyword.kwlist
                lst_ = [a for a in lst_ if a.startswith(complete)]
                lst_.sort()
            except:
                lst_ += keyword.kwlist
                lst_ = [a for a in lst_ if a.startswith(complete)]
                lst_.sort()
        else:
            mod = True
            complete = self.get_context(iter2)
            if complete.isdigit():
                return
            if len(complete.strip()) > 0:
                try:
                    lst_ = [str(a[0]) for a in importsTipper.GenerateTip(complete, os.path.dirname(complete)) if a is not None]
                except:
                    try:
                        c = compile(text_code, '<string>', 'exec')
                        lst_ = [a for a in c.co_names if a.startswith(complete)]
                        con = map(str, c.co_consts)
                        con = [a for a in con if a.startswith(complete) and a not in lst_]
                        lst_ += con
                        lst_ += keyword.kwlist
                        lst_ = [a for a in lst_ if a.startswith(complete)]
                        lst_.sort()
                        complete = ""
                    except:
                        lst_ += keyword.kwlist
                        lst_ = [a for a in lst_ if a.startswith(complete)]
                        lst_.sort()
                        complete = ""
        if len(lst_)==0:
            return
        cw = AutoCompletionWindow(editor, iter2, complete, 
                                    lst_, 
                                    mw, 
                                    mod, 
                                    self.context_bounds)
