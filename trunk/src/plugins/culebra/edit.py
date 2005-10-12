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

# This file is part of Culebra plugin.

import gtk
import gtk.gdk
import gobject
import sys, os
import pango
import dialogs
import gtksourceview
import gnomevfs
import importsTipper
import keyword
import weakref
import codecs

from events import *
from components import *
import components as binding

BLOCK_SIZE = 2048

RESPONSE_FORWARD     = 0
RESPONSE_BACK        = 1
RESPONSE_REPLACE     = 2
RESPONSE_REPLACE_ALL = 3

KEY_ESCAPE = gtk.gdk.keyval_from_name ("Escape")

#################
# gtk.TextBuffer utility functions
def get_buffer_selection (buffer):
    """Returns the selected text, when nothing is selected it returns the empty
    string."""
    bounds = buffer.get_selection_bounds()
    if bounds == ():
        return ""
    else:
        return buffer.get_slice(*bounds)

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
    
######################
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
            self._no_more_entries ()
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
        Component.__init__ (self, None)
        
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

def hide_on_delete (window):
    """
    Makes a window hide it self instead of getting destroyed.
    """
    
    def on_delete (wnd, *args):
        wnd.hide ()
        return True
        
    return window.connect ("delete-event", on_delete)

class CulebraView(gtksourceview.SourceView):
    def __init__(self):
        
        gtksourceview.SourceView.__init__(self)
            
        self.set_auto_indent(True)
        self.set_show_line_numbers(True)
        self.set_show_line_markers(True)
        self.set_tabs_width(4)
        self.set_margin(80)
        self.set_show_margin(True)
        self.set_smart_home_end(True)
        self.set_highlight_current_line(True)
        font_desc = pango.FontDescription('monospace 10')
        if font_desc is not None:
            self.modify_font(font_desc)

class GotoLineComponent (binding.Component):

    action_group = binding.Obtain ("../ag")
    
    goto_line = binding.Make (
        lambda self: self.action_group.get_action ("GotoLine")
    )

    def _init (self):
        
        dialog = gtk.Dialog("", self.parent.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_JUMP_TO, RESPONSE_FORWARD))
        self.dialog = dialog
        hide_on_delete (dialog)
        dialog.connect("response", self.on_dialog_response)
        dialog.set_default_response(RESPONSE_FORWARD)
        dialog.set_border_width (12)
        dialog.set_has_separator (False)
        dialog.action_area.set_border_width (0)
        
        hbox = gtk.HBox ()
        hbox.show ()
        hbox.set_spacing (6)
        dialog.vbox.add (hbox)
        
        lbl = gtk.Label ()
        lbl.set_markup_with_mnemonic ("_Line number:")
        lbl.show ()
        hbox.pack_start (lbl, False, False)
        
        line_text = gtk.Entry()
        self.line_text = line_text
        line_text.set_activates_default(True)
        line_text.connect ("changed", self.on_text_changed)
        line_text.show()
        hbox.pack_start (line_text, False, False)
        
        self.on_text_changed (self.line_text)
        
        self.goto_line.connect ("activate", self.on_goto_line)
        
    def on_dialog_response (self, dialog, response_id):
        if response_id == gtk.RESPONSE_CLOSE:
            dialog.hide ()
            return

        line = self.line_text.get_text()
        if not line.isdigit():
            return
            
        buff = self.parent.get_current()
        titer = buff.get_iter_at_line(int(line)-1)
        self.parent.editor.scroll_to_iter(titer, 0.25)
        buff.place_cursor(titer)
        
        # hide when we find something
        self.parent.editor.grab_focus()
        dialog.hide ()
    
    def on_text_changed (self, entry):
        
        is_sensitive = self.line_text.get_text ().isdigit ()
        self.dialog.set_response_sensitive (RESPONSE_FORWARD, is_sensitive)
    
    def on_goto_line (self, edit_window):
        self.line_text.select_region (0, -1)
        self.line_text.grab_focus()
       
        self.dialog.run()
        self.line_text.grab_focus()


class ToolbarObserver (object):
    """We must use one instance of this class for each buffer that is assigned."""
    def __init__ (self, **kwargs):
        for attr, val in kwargs.iteritems ():
            setattr (self, attr, val)

    def on_can_undo (self, buffer, can_undo):
        self.undo.set_sensitive (can_undo)
    
    def on_can_redo (self, buffer, can_redo):
        self.redo.set_sensitive (can_redo)
    
    def on_modified_changed (self, buff):
        is_sensitive = buff.get_modified () or buff.is_new
        self.save.set_sensitive (is_sensitive)
        self.save_as.set_sensitive (is_sensitive)
        self.update_close (buff)
    
    def update_close (self, *args):
        manager = self.edit_window.entries
        is_sensitive = not (len (manager) == manager.count_new () == 1) 
        self.close.set_sensitive (is_sensitive)
    
    def update_selection_sensitive (self, buff):
        has_selection = buff.get_selection_bounds() != ()
        self.cut.set_sensitive (has_selection)
        self.copy.set_sensitive (has_selection)
    
    def update_revert (self, *args):
        self.revert.set_sensitive (not self.buffer.is_new)
    
    def on_mark_set (self, buff, textiter, mark):
        if mark.get_name () in ("insert", "selection-bound"):
            self.update_selection_sensitive (buff)
            
    def observe (self, buff):
        self.buffer = buff
        self.sources = []
        self.sources.append(buff.connect("can-redo", self.on_can_redo))
        self.sources.append(buff.connect("can-undo", self.on_can_undo))
        self.sources.append(
            buff.connect("modified-changed", self.on_modified_changed)
        )
        self.sources.append(buff.connect("mark-set", self.on_mark_set))
        
        self.events.register ("buffer-closed-event", self.update_close)
        
        self.sources.append (
            self.save.connect ("activate", self.update_revert)
        )
        self.sources.append (
            self.save_as.connect ("activate", self.update_revert)
        )
        self.on_can_undo(buff, buff.can_undo ())
        self.on_can_redo(buff, buff.can_redo ())
        self.on_modified_changed (buff)
        self.update_selection_sensitive (buff)
    
    def unobserve (self):
        if not hasattr (self, "sources"):
            return

        for source_id in self.sources:
            gobject.source_remove (source_id)
        
        self.events.unregister ("buffer-closed-event", self.update_close)
        del self.sources
    
class ToolbarSensitivityComponent (Component):
    def _init (self):
        
        self.observer = None
        ag = self.parent.ag

        self.elements = dict (
            save        = ag.get_action ("FileSave"),
            save_as     = ag.get_action ("FileSaveAs"),
            revert      = ag.get_action ("FileRevert"),
            undo        = ag.get_action ("EditUndo"),
            redo        = ag.get_action ("EditRedo"),
            close       = ag.get_action ("Close"),
            cut         = ag.get_action ("EditCut"),
            paste       = ag.get_action ("EditPaste"),
            copy        = ag.get_action ("EditCopy"),
            edit_window = self.parent,
            events      = self.parent.events,
        )
        
        self.script_execute = ag.get_action ("RunScript")
        self.script_break   = ag.get_action ("StopScript")
        self.next_buffer    = ag.get_action ("NextBuffer")
        self.prev_buffer    = ag.get_action ("PrevBuffer")
        self.revert         = ag.get_action ("FileRevert")
        
        self.parent.events.register ("buffer-changed", self.on_buffer_changed)
        events = self.parent.entries.events
        events.register ("selection-changed", self.on_selection_changed)
        
        self.on_buffer_changed (self.parent, self.parent.get_current())
        self.on_selection_changed ()
    
    def on_selection_changed (self, *args):
        self.next_buffer.set_sensitive (self.parent.entries.can_select_next ())
        self.prev_buffer.set_sensitive (self.parent.entries.can_select_previous())

    def on_buffer_changed (self, old_buff, buff):
        is_sensitive = buff.get_language ().get_name () == "Python"
        self.script_execute.set_sensitive (is_sensitive)
        self.script_break.set_sensitive (is_sensitive)
        
        self.revert.set_sensitive (not buff.is_new)
        if self.observer is not None:
            self.observer.unobserve ()

        obs = ToolbarObserver (**self.elements)
        obs.observe (buff)
        self.observer = obs

class BufferManager (object):
    """
    This manages the mechanichs of manipulating the list of BufferEntries.
    It's basically an observable list that suports item selecting.
    You can access the entries by the 'entries' variable, for most methods,
    directly to this class, since the '__getitem__', '__len__' and '__iter__'
    map to the internal list.
    """
    
    def __init__ (self):
        self._entries = []

        self.events = EventsDispatcher()
        self.__evts_srcs = self.events.create_events (("add-entry", "remove-entry", "selection-changed"))
        self.__selected_index = -1
        
    def count_new (self):
        counter = 0
        for entry in self:
            if entry.is_new:
                counter += 1
        return counter
    
    def append (self, buff):
        self._entries.append (buff)
        self.__evts_srcs["add-entry"](buff)
    
    def remove (self, buff):
        old_index = self.selected_index
        old_value = self.selected
        
        self._entries.remove (buff)
        
        # If the old selected value was removed then clear the selection
        if old_value is buff:
            self.__selected_index = -1
            self.__evts_srcs["selection-changed"](old_index, old_value, -1, None)
        
        # If the selected value changed then make it equal again
        elif old_value is not self.__selected_index:
            self.__selected_index = self._entries.index (old_value)
            self.__evts_srcs["selection-changed"](old_index, old_value, self.selected_index, old_value)
    
    def __delitem__ (self, index):
        buff = self._entries[index]
        self.remove (buff)
    
    def set_selected_index (self, index):
        # When the index maintained then do nothing
        if self.__selected_index == index:
            return
        old_index = self.__selected_index
        old_value = self.get_selected()
        
        self.__selected_index = index
        self.__evts_srcs["selection-changed"](old_index, old_value, index, self.selected)
    
    def get_selected_index (self):
        return self.__selected_index
    
    def unset_selected_index (self):
        self.__selected_index = -1
    
    selected_index = property (get_selected_index, set_selected_index, unset_selected_index)
    
    def get_selected (self):
        if self.selected_index == -1:
            return None
        assert self.selected_index < len (self._entries), "Selected index %d, %r" % (self.selected_index, self._entries)
        return self._entries[self.selected_index]
    
    def unset_selected (self):
        del self[self.selected_index]
    
    def set_selected (self, entry):
        self.selected_index = self._entries.index (entry)
    
    selected = property (get_selected, set_selected, unset_selected)
    
    def __getitem__ (self, key):
        return self._entries[key]
    
    def __len__ (self):
        return len (self._entries)
    
    def __contains__ (self, entry):
        return entry in self.entries

    def __iter__ (self):
        return iter (self._entries)
    
    def can_select_next (self):
        return self.selected_index != -1 \
               and self.selected_index + 1 < len (self._entries)
        
    def select_next (self):
        assert self.can_select_next ()
        self.selected_index += 1
    
    def can_select_previous (self):
        return self.selected_index != -1 and self.selected_index > 0
    
    def select_previous (self):
        assert self.can_select_previous ()
        self.selected_index -= 1

    def index (self, entry):
        return self._entries.index (entry)

    def __repr__ (self):
        return repr (self._entries)

class BufferManagerListener (binding.Component):
    entries = binding.Obtain("../entries")
    
    # This component depends on the 'events' object and both are created
    # upon assembly, therefore obtaining the 'events' object upon this component's
    # assembly we create the dependency 
    __depends = binding.Obtain ("../events", uponAssembly = True)
    
    def _init (self):
        evts = self.entries.events
        evts.register ("selection-changed", self.on_selection_changed)
        evts.register ("add-entry", self.on_add_entry)
        evts.register ("remove-entry", self.on_remove_entry)
        self.last_index = self.entries.selected_index
        
        self.entries.append (CulebraBuffer())
    
    def on_selection_changed (self, old_index, old_value, index, value):
        
        # If we lost our selection then select the last selected index
        if index == -1:
        
            if self.last_index == -1 or self.last_index >= len (self.entries):
                self.entries.selected_index = len (self.entries) - 1
            else:
                self.entries.selected_index = self.last_index
       
        self.last_index = index
        
        if value is None:
            return
            
        # Set bind the SourceView to the SourceBuffer
        self.parent.editor.set_buffer (value)
        # and add focus to it
        self.parent.editor.grab_focus()
        
        self.parent._buffer_changed(old_value, self.entries.selected)
        
    def on_add_entry (self, buff):
        # We move the focus to the last selected index
        self.entries.selected = buff

        buff.connect('insert-text', self.on_insert_text)
        

    def on_insert_text (self, buff, it, text, length):
        if self.parent.use_autocomplete:
            buff.show_completion (text,
                                  it,
                                  self.parent.editor,
                                  self.parent.plugin.pida.mainwindow)
        
    def on_remove_entry (self, entry, index):
        # If we have 0 entries then we add one
        if len (self.entries) == 0:
            self.entries.append (CulebraBuffer())
        
class SearchBar (binding.Component):
    action_group = binding.Obtain ("../ag")
    
    find_forward = binding.Make (
        lambda self: self.action_group.get_action ("EditFindNext")
    )
    
    find_backward = binding.Make (
        lambda self: self.action_group.get_action ("EditFindBack")
    )
    
    find = binding.Make (
        lambda self: self.action_group.get_action ("EditFind")
    )
    
    set_active = binding.Obtain ("find/set_active")
    get_active = binding.Obtain ("find/get_active")
    
    def widget (self):

        hbox = gtk.HBox (spacing = 6)
        hbox.connect ("show", self.on_show)
        hbox.connect ("hide", self.on_hide)
        hbox.connect ("key-release-event", self.on_key_pressed)
        
        lbl = gtk.Label ("Search:")
        lbl.show ()
        hbox.pack_start (lbl, expand = False, fill = False)
        
        entry = gtk.Entry ()
        entry.connect ("changed", self.on_entry_changed)
        entry.connect ("focus", self.on_entry_focus)
        entry.connect ("activate", self.on_entry_activate)
        entry.show ()
        entry.set_activates_default(True)
        self.entry = entry
        hbox.pack_start (entry, expand = False, fill = False)

        # Find backwards
        btn_back = gtk.Button (stock = gtk.STOCK_GO_BACK)
        btn_back.show ()
        self.find_backward.connect_proxy (btn_back)
        hbox.pack_start (btn_back, expand = False, fill = False)

        # Find forward
        btn_forward = gtk.Button (stock = gtk.STOCK_GO_FORWARD)
        btn_forward.show ()
        self.btn_forward = btn_forward
        self.find_forward.connect_proxy (btn_forward)
        hbox.pack_start (btn_forward, expand = False, fill = False)
        
        self.find.connect ("toggled", self.on_find)

        self.parent.events.register ("buffer-changed", self.on_buffer_changed)

        return hbox
        
    widget = binding.Make (widget)
    
    def bind (self, buff):
        buff.search.events.register ("changed", self.on_search_changed)
        buff.search.search_text = self.entry.get_text ()
        buff.search.enable()
    
    def unbind (self, buff):
        buff.search.events.unregister ("changed", self.on_search_changed)
        buff.search.disable()
    
    def on_entry_changed (self, entry):
        is_sensitive = entry.get_text () != ""
        self.find_forward.set_sensitive (is_sensitive)
        self.find_backward.set_sensitive (is_sensitive)
        self.parent.get_current().search.search_text = entry.get_text ()
    
    def on_clicked (self, btn):
        buff = self.parent.get_current ()
        buff.search_text = self.entry.get_text ()
    
    def on_entry_activate (self, entry, *args):
        self.btn_forward.activate ()

    def on_show (self, dialog):
        self.bind (self.parent.get_current())
        self.entry.select_region(0, -1)
        self.entry.grab_focus()

    
    def on_hide (self, dialog):
        self.unbind (self.parent.get_current())
    
    def on_key_pressed (self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.set_active (False)
    
    def on_find (self, action):
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()

    def on_entry_focus (self, entry, *args):
        # Select all
        entry.select_region (0, -1)

    def on_buffer_changed (self, old_buff, buff):
        if old_buff is not None:
            self.unbind(old_buff)
        if buff is not None:
            self.bind(buff)

    def on_search_changed (self, text):
        self.entry.set_text (text)
         
class ReplaceBar (binding.Component):
    """
    This component implements an event that validates when the selection is
    synchronized with the selected text.
    """
    action_group = binding.Obtain ("../ag")

    search_bar = binding.Obtain ("../search_bar")
    
    get_current = binding.Obtain ("../get_current")

    def get_replace_text (self):
        return self._replace_entry.get_text ()
    
    replace_text = property (get_replace_text)
        
    replace = binding.Make (
        lambda self: self.action_group.get_action ("EditReplace")
    )
    replace_next = binding.Make (
        lambda self: self.action_group.get_action ("EditReplaceNext")
    )
    replace_all = binding.Make (
        lambda self: self.action_group.get_action ("EditReplaceAll")
    )
    
    def widget (self):
        hig_add = lambda container, widget: \
                  container.pack_start (widget, expand = False, fill = False)
        
        hbox = gtk.HBox (spacing = 6)
        hbox.connect ("key-release-event", self.on_key_pressed)
        hbox.connect ("show", self.on_show)
        hbox.connect ("hide", self.on_hide)
        
        lbl = gtk.Label("Replace")
        lbl.show()
        hig_add (hbox, lbl)
        
        entry = gtk.Entry()
        entry.show ()
        entry.connect("changed", self.on_entry_changed)
        self._replace_entry = entry
        hig_add (hbox, entry)
        
        btn = gtk.Button (stock = gtk.STOCK_FIND_AND_REPLACE)
        self.replace_next.connect_proxy (btn)
        btn.show()
        hig_add (hbox, btn)
        
        btn = gtk.Button (stock = gtk.STOCK_FIND_AND_REPLACE)
        btn.set_label ("Replace All")
        self.replace_all.connect_proxy (btn)
        btn.show()
        hig_add (hbox, btn)

        self.replace_next.connect ("activate", self.on_replace_curr)
        self.replace_all.connect ("activate", self.on_replace_all)
        self.parent.events.register ("buffer-changed", self.on_buffer_changed)

        self.replace.connect ("toggled", self.on_replace)
        self.search_bar.widget.connect ("key-release-event", self.on_key_pressed)
        
        return hbox
        
    widget = binding.Make (widget)

    def bind (self, buff):
        buff.replace.events.register ("changed", self.on_replace_changed)
        buff.replace.replace_text = self._replace_entry.get_text ()
    
    def unbind (self, buff):
        buff.replace.events.unregister ("changed", self.on_replace_changed)

    def on_show (self, dialog):
        self.search_bar.find.set_active (True)
        self.search_bar.find.set_sensitive (False)
        self.bind(self.get_current())
    
    def on_hide (self, dialog):
        self.search_bar.find.set_active (False)
        self.search_bar.find.set_sensitive (True)
        self.unbind(self.get_current())
    
    def on_key_pressed (self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.replace.set_active (False)

    def on_replace (self, action):
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()
        
    def on_replace_curr (self, btn):
        self.get_current().replace()
        self.get_current().search()
    
    def on_replace_all (self, btn):
        self.get_current().replace_all()
        
    def on_entry_changed (self, entry):
        self.get_current().replace.replace_text = entry.get_text()
    
    def on_buffer_changed (self, old_buff, buff):
        if old_buff is not None:
            self.unbind(old_buff)
        if buff is not None:
            self.bind(buff)
    
    def on_replace_changed (self, text):
        self._replace_entry.set_text (text)
        
        
class EditWindow(Component, gtk.EventBox):
    
    # If the user access the event sources, the 'events' field is created
    # and vice-versa
    _buffer_changed = binding.Make (
        lambda self: self.events.create_event("buffer-changed")
    )
    
    _buffer_closed = binding.Make (
        lambda self: self.events.create_event("buffer-changed")
    )
    
    def events (self):
        events = EventsDispatcher()
        self._buffer_changed = events.create_event("buffer-changed")
        self._buffer_closed  = events.create_event("buffer-closed-event")
        return events
        
    events = binding.Make (events, uponAssembly = True)
    
    components = (
        BufferManagerListener, GotoLineComponent,
        ToolbarSensitivityComponent,
        
    )
    
    search_bar = binding.Make (SearchBar)
    replace_bar = binding.Make (ReplaceBar)
    def __init__(self, plugin=None, quit_cb=None):
        gtk.EventBox.__init__(self)
        
        self.plugin = plugin
        self.entries = BufferManager ()
        
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
        self.editor = CulebraView ()
        self.plugin.pida.mainwindow.connect('delete-event', self.file_exit)
        scrolledwin2 = gtk.ScrolledWindow()
        scrolledwin2.add(self.editor)
        self.editor.connect('key-press-event', self.text_key_press_event_cb)
        scrolledwin2.show()
        self.editor.show()
        self.editor.grab_focus()
        
        vbox = gtk.VBox (spacing = 6)
        vbox.show ()
        vbox.add (scrolledwin2)
        vbox.pack_start (self.search_bar.widget, expand = False, fill = False)
        vbox.pack_start (self.replace_bar.widget, expand = False, fill = False)
        
        self.hpaned.add2(vbox)
        self.hpaned.set_position(200)
        self.dirty = 0
        self.clipboard = gtk.Clipboard(selection='CLIPBOARD')
        self.dirname = "."
        # sorry, ugly
        self.filetypes = {}
        
        Component.__init__ (self)
    
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
            ('Close', gtk.STOCK_CLOSE, None, None, "Close current file", self.file_close),
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
            ('GotoLine', gtk.STOCK_JUMP_TO, 'Goto Line', '<control>g', 
                 None, self.goto_line),
            ('RunMenu', None, '_Run'),
            ('RunScript', gtk.STOCK_EXECUTE, None, "F5","Run script", self.run_script),
            ('StopScript', gtk.STOCK_STOP, None, "<ctrl>F5","Stop script execution", self.stop_script),
            ('DebugScript', None, "Debug Script", "F7",None, self.debug_script),
            ('DebugStep', None, "Step", "F8",None, self.step_script),
            ('DebugNext', None, "Next", "<shift>F7",None, self.next_script),
            ('DebugContinue', None, "Continue", "<control>F7", None, self.continue_script),
            ('BufferMenu', None, '_Buffers'),
            ('PrevBuffer', gtk.STOCK_GO_UP, None, "<shift>F6","Previous buffer", self.prev_buffer),
            ('NextBuffer', gtk.STOCK_GO_DOWN, None, "F6","Next buffer", self.next_buffer),
            ('HelpMenu', None, '_Help'),
            ('About', gtk.STOCK_ABOUT, None, None, None, self.about),
            ]
        self.ag = gtk.ActionGroup('edit')
        self.ag.add_actions(actions)
        self.ag.add_toggle_actions ((
            ('EditFind', gtk.STOCK_FIND, "Find...", None, "Search for text", None),
            ('EditReplace', gtk.STOCK_FIND_AND_REPLACE, "_Replace...", '<control>h', 
                "Search for and replace text", None),
        ))
        for action_name in ("FileOpen", "FileSave", "EditUndo", "RunScript"):
            action = self.ag.get_action (action_name)
            action.set_property ("is-important", True)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(self.ag, 0)
        self.ui.add_ui_from_string(ui_string)
        
        toolbar = self.ui.get_widget ("/toolbar")
        toolbar.set_property ("show-arrow", False)
        
        self.get_parent_window().add_accel_group(self.ui.get_accel_group())
        return (self.ui.get_widget('/menubar'), toolbar)
    
    __use_autocomplete = False
    def get_use_autocomplete(self):
        return self.__use_autocomplete
    
    def set_use_autocomplete(self, value):
        self.__use_autocomplete = value
    
    use_autocomplete = property (get_use_autocomplete, set_use_autocomplete)
    
    def about(self, mi):
        d = gtk.AboutDialog()
        d.set_name('Culebra Editor')
        d.set_version('0.2.3')
        d.set_copyright('Copyright © 2005 Fernando San Martín Woerner')
        d.set_comments('This plugin works as a text editor inside PIDA')
        d.set_authors(['Fernando San Martín Woerner (fsmw@gnome.org)',
                        'Ali Afshar (aafshar@gmail.com) ',
                        'Tiago Cogumbreiro (cogumbreiro@users.sf.net)'])
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
        self.context_bounds = (buff.create_mark('cstart',it), buff.create_mark('cend',iter2))
        if prev in (".", "_"):
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
                data = fd.read ()
                enc_data = None
                for enc in (sys.getdefaultencoding(), "utf-8", "iso8859", "ascii"):
                    try:
                        enc_data = unicode (data, enc)
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
                traceback.print_exc ()
                
                print sys.exc_info()[1]
                resp = dlg.run()
                dlg.hide()
                return
            self.entries.append (buff)

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
        
        # If the opened entry is not the selected one then select it
        if buff is not self.get_current ():
            self.plugin.do_edit('changebuffer', self.entries.index (buff))
    
        if new_entry:
            self.plugin.do_edit('getbufferlist')
            self.plugin.do_edit('getcurrentbuffer')

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
        buff = CulebraBuffer ()
        buff.set_text("")
        buff.set_modified(False)

        manager = buff.languages_manager
        language = manager.get_language_from_mime_type("text/x-python")
        buff.set_highlight(True)
        buff.set_language(language)

        self.entries.append (buff)

        self.plugin.do_edit('getbufferlist')
        self.plugin.do_edit('getcurrentbuffer')
        self.plugin.do_edit('changebuffer', len(self.entries) - 1)

    def file_open(self, mi=None):
            
        fn = self.get_current().filename
        dirn = os.path.dirname(fn)
        fname = dialogs.OpenFile('Open File', self.get_parent_window(),
                                  dirn, None, "*.py")
        
        if fname is None:
            return
        
        first_entry = self.entries[0]
        new_and_changed = first_entry.is_new and first_entry.get_modified ()
        
        if len (self.entries) == 1 and new_and_changed and self.chk_save ():
            return
            
        self.load_file(fname)
        self.plugin.pida.mainwindow.set_title(os.path.split(fname)[1])

    def file_save(self, mi=None, fname=None):
            
        buff = self.get_current ()
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

        self.check_mime(self.entries.selected)
        self.plugin.do_edit('getbufferlist')
        self.plugin.do_edit('getcurrentbuffer')
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
    
    def file_revert (self, *args):
        # XXX: the save dialog is totally inapropriate, should be a revert dialog
        self.chk_save ()
        self.load_file (self.get_current ().filename)
    
    def file_close(self, mi=None, event=None):
        self.chk_save ()
        del self.entries.selected
        self.plugin.do_edit('getbufferlist')
        self.plugin.do_edit('getcurrentbuffer')
        self._buffer_closed ()

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

    def edit_find_next(self, action = None):
        self.get_current().search (editor = self)
    
    def edit_find_back (self, action = None):
        self.get_current().search (editor = self, find_forward = False)
        
    def goto_line(self, mi=None):
        self.emit ("goto-line-event")

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
        if self.entries.can_select_next ():
            self.entries.select_next ()
            self.plugin.do_edit('changebuffer', self.entries.selected_index)

    def prev_buffer(self, mi):
        if self.entries.can_select_previous ():
            self.entries.select_previous ()
            self.plugin.do_edit('changebuffer', self.entries.selected_index)

gobject.type_register(EditWindow)
        
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
