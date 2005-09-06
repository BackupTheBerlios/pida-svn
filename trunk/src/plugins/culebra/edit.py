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

BLOCK_SIZE = 2048

RESPONSE_FORWARD = 0
RESPONSE_BACKWARD = 1
RESPONSE_REPLACE = 2
RESPONSE_REPLACE_ALL = 3

KEY_ESCAPE = gtk.gdk.keyval_from_name ("Escape")

class CulebraBuffer(gtksourceview.SourceBuffer):

    def __init__(self, filename = None):
        gtksourceview.SourceBuffer.__init__(self)
        lm = gtksourceview.SourceLanguagesManager()
        self.languages_manager = lm
        self.save = False
        language = lm.get_language_from_mime_type("text/x-python")
        self.set_highlight(True)
        self.set_language(language)
        self.search_string = None
        self.search_mark = self.create_mark('search', self.get_start_iter())
        self.__filename = filename
    
    def get_filename (self):
        if self.__filename is None:
            return "New File"
        return self.__filename
    
    def set_filename (self, filename):
        self.__filename = filename
    
    filename = property (get_filename, set_filename)
    
    def get_is_new (self):
        return self.__filename is None
    
    is_new = property (get_is_new)
        
    def search(self, search_string, mark = None, scroll=True, editor = None):
        if mark is None:
            start = self.get_start_iter()
        else:
            start = self.get_iter_at_mark(mark)
        i = 0
        if search_string:
            if self.search_string != search_string:
                start = self.get_start_iter()
            self.search_string = search_string
            res = start.forward_search(search_string, gtk.TEXT_SEARCH_TEXT_ONLY)
            if res:
                match_start, match_end = res
                if scroll and editor is not None:
                    editor.scroll_to_iter(match_start, 0.25)
                self.place_cursor(match_start)
                self.select_range(match_start, match_end)
                self.move_mark(self.search_mark, match_end)
                return True
            else:
                start = self.get_start_iter()
                res = start.forward_search(search_string, gtk.TEXT_SEARCH_TEXT_ONLY)
                if res:
                    match_start, match_end = res
                    if scroll and editor is not None:
                        editor.scroll_to_iter(match_start, 0.25)
                    self.place_cursor(match_start)
                    self.select_range(match_start, match_end)
                    self.move_mark(self.search_mark, match_end)
                    return True
                self.search_string = None
                self.move_mark(self.search_mark, self.get_start_iter())
        return False
        
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

def get_buffer_selection (buffer):
    """Returns the selected text, when nothing is selected it returns the empty
    string."""
    bounds = buffer.get_selection_bounds()
    if bounds == ():
        return ""
    else:
        return buffer.get_slice(*bounds)

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

void_func = lambda *args: None

class Component (object):
    """
    A Component is an object that is structured in a hierarchical model.
    It is constructed upon runtime from the root to its children. To define
    a Component you have to define a list of subcomponents, these are usually
    classes of this type.
    They define a method called '_init' that is called in the constructor.
    It also contains a '_components' protected variable that holds a list of its
    children components.
    """
    
    def __init__ (self, parent = None):
        self.__parent = parent is not None and weakref.ref (parent) or void_func
        # Maintain components reference
        self._components = []
        for component in self.components:
            self._components.append (component(self))
            
        self._init ()
    
    def _init (self):
        """Override this method which is called in the constructor."""
    
    def getParent (self):
        return self.__parent ()
        
    parent = property (getParent)
    
    components = ()

class GotoLineComponent (Component):
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
        
        self.parent.connect ("goto-line-event", self.on_goto_line)
        
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


class SearchReplaceComponent (Component):
    """
    This class aggregates all code related to Search & Replace functionality.
    """
    
    def _init (self):
        # Construct the GUI
        self.dialog = gtk.Dialog("", self.parent.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            ("Replace", RESPONSE_REPLACE,
                             "Replace All", RESPONSE_REPLACE_ALL,
                             gtk.STOCK_FIND, RESPONSE_FORWARD))
        
        hide_on_delete (self.dialog)
        self.dialog.set_has_separator (False)
        self.dialog.vbox.set_border_width (12)
        self.dialog.set_resizable (False)
        self.dialog.set_default_response(RESPONSE_FORWARD)
        self.dialog.connect ("response", self.replace_dialog_response_cb)
        
        tbl = gtk.Table ()
        tbl.set_border_width (12)
        tbl.show ()
        tbl.set_row_spacings (12)
        tbl.set_col_spacings (6)
        self.dialog.vbox.add (tbl)
        
        self.search_text = gtk.Entry()
        self.search_text.connect ("key-release-event", self.on_key_pressed)
        self.search_text.show()
        self.search_text.set_activates_default(True)
        # The search entry affects the replace, replace all and find buttons
        # when it has text they can be sensitive
        self.search_text.connect("changed", self.on_search_text_changed)
        self.search_text.connect ("focus", self.on_search_focus)

        self.replace_text = gtk.Entry() 
        self.replace_text.connect ("key-release-event", self.on_key_pressed)
        self.replace_text.show()
        self.replace_text.set_activates_default(True)
        
        lbl = gtk.Label("Search for:")
        lbl.set_alignment (1, 0)
        lbl.show ()
        tbl.attach (lbl, 0, 1, 0, 1)
        tbl.attach (self.search_text, 1, 2, 0, 1, gtk.SHRINK)

        lbl = gtk.Label("Replace with:")
        lbl.set_alignment (1, 0)
        lbl.show ()
        tbl.attach (lbl, 0, 1, 1, 2)
        tbl.attach (self.replace_text, 1, 2, 1, 2, gtk.SHRINK)

        self.replace_button = self.dialog.action_area.get_children ()[2]
        self.replace_all_button = self.dialog.action_area.get_children ()[1]

        self.find_button = self.dialog.action_area.get_children ()[0]
        # The replace button should only be sensitive if there is selected
        # text and if that text equals the searched text
        self.find_button.connect ("clicked", self.on_find_clicked)

        self.parent.connect ("search-replace-event", self.on_search_replace)

        # Update sensitiveness
        self.on_search_text_changed()
    
    
    def get_buffer (self):
        return self.parent.get_current()
    
    buffer = property(get_buffer)
    
    def get_buffer_selection (self):
        return get_buffer_selection (self.buffer)
        
    buffer_selection = property(get_buffer_selection)
    
    def replace_button_sensitivity (self):
        is_sensitive = self.buffer_selection == self.search_text.get_text () \
                       and self.search_text.get_text () != ""
                       
        self.replace_button.set_sensitive (is_sensitive)
    
    def on_search_focus (self, *args):
        # Select all
        self.search_text.select_region (0, -1)
    
    def on_search_replace (self, *args):
        if self.buffer_selection != "":
            self.search_text.set_text(self.buffer_selection)
        self.replace_button_sensitivity ()
        self.search_text.select_region (0, -1)
        self.search_text.grab_focus()
        self.dialog.run ()
    
        
    def on_search_text_changed (self, *args):
        is_sensitive = len(self.search_text.get_text ()) > 0
        self.replace_button.set_sensitive(False)
        self.replace_all_button.set_sensitive(is_sensitive)
        self.find_button.set_sensitive (is_sensitive)
    
    def on_find_clicked (self, *args):
        selected_text = get_buffer_selection (self.buffer)
        is_sensitive = selected_text != self.search_text.get_text ()
        self.replace_button_sensitivity ()

    def replace_dialog_response_cb (self, dialog, response_id):
        search_text = self.search_text
        replace_text = self.replace_text
        buff = self.buffer
            
        if response_id == gtk.RESPONSE_CLOSE:
            self.dialog.hide ()

        elif response_id == RESPONSE_FORWARD:
            buff.search(search_text.get_text(), buff.search_mark, editor=self.parent.editor)

        elif response_id == RESPONSE_REPLACE:
            # get selection
            selected_text = self.buffer_selection

            if selected_text != "" and selected_text != search_text.get_text ():
                return
                
            start, end = self.buffer.get_selection_bounds ()
            buff.delete(start, end)
            buff.insert(start, replace_text.get_text())
            start = buff.get_iter_at_mark(buff.get_insert())
            start.backward_chars(len(replace_text.get_text()))
            buff.search(search_text.get_text(), buff.search_mark, editor=self.parent.editor)

        elif response_id == RESPONSE_REPLACE_ALL:
            current_iter = buff.get_iter_at_mark(buff.get_insert())
            while buff.search(search_text.get_text(), buff.search_mark, False, self.parent.editor):
                start, end = buff.get_selection_bounds()
                buff.delete(start, end)
                buff.insert(start, replace_text.get_text())
                start = buff.get_iter_at_mark(buff.get_insert())
                start.backward_chars(len(replace_text.get_text()))
                buff.select_range(start, buff.get_iter_at_mark(buff.search_mark))

            if current_iter is not None:
                buff.place_cursor(current_iter)
        self.replace_button_sensitivity ()

    def on_key_pressed (self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.dialog.hide ()

class SearchComponent (Component):
    
    def get_search_text (self):
        return self._search_text.get_text ()
    
    def set_search_text (self, text):
        self._search_text.set_text (text)
    
    search_text = property (get_search_text, set_search_text)
    
    def _init (self):
        self.parent.connect ("search-event", self.on_search_dialog)
        
        self.dialog = gtk.Dialog("", self.parent.get_parent_window(),
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_FIND, RESPONSE_FORWARD))
        hide_on_delete (self.dialog)
        self.dialog.set_default_response(RESPONSE_FORWARD)
        self.dialog.set_has_separator (False)
        self.dialog.set_resizable (False)
        self.dialog.connect ("response", self.on_dialog_response)

        hbox = gtk.HBox ()
        hbox.set_border_width (10)
        hbox.set_spacing (6)
        hbox.show ()
        self.dialog.vbox.add (hbox)
        
        lbl = gtk.Label ("Search for:")
        lbl.set_alignment (0, 0.5)
        lbl.show ()
        hbox.pack_start (lbl, False, False)
        
        self._search_text = gtk.Entry()
        self._search_text.set_activates_default(True)
        self._search_text.show()
        self._search_text.grab_focus()
        self._search_text.connect ("key-release-event", self.on_key_pressed)
        self._search_text.connect ("changed", self.on_search_text_changed)
        hbox.pack_start (self._search_text, False, False)

        self.find_button = self.dialog.action_area.get_children ()[0]
        
        self.on_search_text_changed ()
    
    def on_dialog_response (self, dialog, response):
        # Hide when the user closes the window
        if response != RESPONSE_FORWARD:
            dialog.hide ()
        
        # Search forward
        if response == RESPONSE_FORWARD:
            self.parent.buffer.search(
                self.search_text, 
                self.parent.get_current().search_mark, 
                editor=self.parent.editor
            )
        
    def on_search_dialog (self, *args):
        # Update search text dialog
        selected_text = get_buffer_selection (self.parent.get_current())
        if selected_text != "":
            self.search_text = selected_text 

        self._search_text.select_region (0, -1)
        self._search_text.grab_focus()

        self.dialog.run ()
    
    def on_key_pressed (self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.dialog.hide ()
    
    def on_search_text_changed (self, entry = None):
        self.find_button.set_sensitive (self.search_text != "")

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
        self.sources.append (
            self.edit_window.connect ("buffer-closed-event", self.update_close)
        )
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
        )
        
        self.script_execute = ag.get_action ("RunScript")
        self.script_break   = ag.get_action ("StopScript")
        self.next_buffer    = ag.get_action ("NextBuffer")
        self.prev_buffer    = ag.get_action ("PrevBuffer")
        self.revert         = ag.get_action ("FileRevert")
        
        self.parent.connect ("buffer-changed", self.on_buffer_changed)
        events = self.parent.entries.events
        events.register ("selection-changed", self.on_selection_changed)
        
        self.on_buffer_changed (self.parent, self.parent.get_current())
        self.on_selection_changed ()
    
    def on_selection_changed (self, index = None):
        self.next_buffer.set_sensitive (self.parent.entries.can_select_next ())
        self.prev_buffer.set_sensitive (self.parent.entries.can_select_previous())

    def on_buffer_changed (self, parent, buff):
        is_sensitive = buff.get_language ().get_name () == "Python"
        self.script_execute.set_sensitive (is_sensitive)
        self.script_break.set_sensitive (is_sensitive)
        
        self.revert.set_sensitive (not buff.is_new)
        
        if self.observer is not None:
            self.observer.unobserve ()

        obs = ToolbarObserver (**self.elements)
        obs.observe (buff)
        self.observer = obs

class EventsDispatcher(object):
    """
    An event dispatcher is the central events object. To use it you must first
    create an event with the ``create_event`` method, this will return an
    event source which is basically the function you'll use to trigger the
    event. After that you register the callbacks. Its usage follows:
    
    >>> dispatcher = EventDispatcher()
    >>> evt_src = dispatcher.create_event ("on-ring-event")
    >>> 
    >>> def callback1 ():
    >>>     print "riiiing!"
    >>> 
    >>> dispatcher.register_callback ("on-ring-event", callback1)
    >>> 
    >>> evt_src ()
    riiing
    >>> 
    """
    def __init__ (self):
        self.__events = {}
        
    def create_event (self, event_name):
        self.__events[event_name] = []
        
        def event_source (*args, **kwargs):
            for callback in self.__events[event_name]:
                callback (*args, **kwargs)
        
        return event_source
    
    def create_events (self, event_names, event_sources = None):
        """
        This is a utility method that creates or fills a dict-like object
        and returns it. The keys are the event names and the values are the
        event sources.
        """
        if event_sources is None:
            event_sources = {}
            
        for evt_name in event_names:
            event_sources[evt_name] = self.create_event (evt_name)
        return event_sources
    
    def event_exists (self, event_name):
        return event_name in self.__events
    
    def register (self, event_name, callback):
        assert self.event_exists (event_name)
        self.__events[event_name].append (callback)
    
    def unregister (self, event_name, callback):
        self.__events.remove (callback)


class BufferManager (object):
    """
    This manages the mechanichs of manipulating the list of BufferEntries.
    It's basically an observable list that suports item selecting.
    You can access the entries by the 'entries' variable, for most methods,
    directly to this class, since the '__getitem__', '__len__' and '__iter__'
    map to the internal list.
    """
    
    def __init__ (self):
        self.__entries = []

        self.events = EventsDispatcher()
        self.__evts_srcs = self.events.create_events (("add-entry", "remove-entry", "selection-changed"))
        self.__selected_index = -1
        
    def get_entries (self):
        return self.__entries
    
    entries = property (get_entries)
    
    def count_new (self):
        counter = 0
        for entry in self.entries:
            if entry.is_new:
                counter += 1
        return counter
    
    def append (self, buff):
        self.entries.append (buff)
        self.__evts_srcs["add-entry"](buff)
    
    def remove (self, buff):
        index = self.entries.index (buff)
        selected_entry = self.selected
        
        self.entries.remove (buff)
        
        index = self.selected_index
        
        if selected_entry is not buff:
            self.__selected_index = self.entries.index (selected_entry)
        else:
            self.__selected_index = -1
        
        self.__evts_srcs["remove-entry"](buff, index)

        if index != self.selected_index:
            self.__evts_srcs["selection-changed"](self.selected_index)
    
    def __delitem__ (self, index):
        buff = self.entries[index]
        self.remove (buff)
    
    def set_selected_index (self, index):
        # When the index maintained then do nothing
        if self.__selected_index == index:
            return
            
        self.__selected_index = index
        self.__evts_srcs["selection-changed"](index)
    
    def get_selected_index (self):
        return self.__selected_index
    
    def unset_selected_index (self):
        self.__selected_index = -1
    
    selected_index = property (get_selected_index, set_selected_index, unset_selected_index)
    
    def get_selected (self):
        if self.selected_index == -1:
            return None
        assert self.selected_index < len (self.entries), "Selected index %d, %r" % (self.selected_index, self.entries)
        return self.entries[self.selected_index]
    
    def unset_selected (self):
        del self[self.selected_index]
    
    def set_selected (self, entry):
        self.selected_index = self.entries.index (entry)
    
    selected = property (get_selected, set_selected, unset_selected)
    
    def __iter__ (self):
        return iter (self.entries)
    
    def __getitem__ (self, key):
        return self.entries[key]
    
    def __len__ (self):
        return len (self.entries)
    
    def __contains__ (self, entry):
        return entry in self.entries
    
    def can_select_next (self):
        return self.selected_index != -1 \
               and self.selected_index + 1 < len (self.entries)
        
    def select_next (self):
        assert self.can_select_next ()
        self.selected_index += 1
    
    def can_select_previous (self):
        return self.selected_index != -1 \
               and self.selected_index > 0
    
    def select_previous (self):
        assert self.can_select_previous ()
        self.selected_index -= 1

    def index (self, entry):
        return self.__entries.index (entry)

    def __repr__ (self):
        return repr (self.__entries)

class BufferManagerListener (Component):
    def _init (self):
        evts = self.entries.events
        evts.register ("selection-changed", self.on_selection_changed)
        evts.register ("add-entry", self.on_add_entry)
        evts.register ("remove-entry", self.on_remove_entry)
        self.last_index = self.entries.selected_index
        
        self.entries.append (CulebraBuffer())
    
    def get_entries (self):
        return self.parent.entries
        
    entries = property (get_entries)
    
    def on_selection_changed (self, index):
        # If we lost our selection then select the last selected index
        if index == -1:
        
            if self.last_index == -1 or self.last_index >= len (self.entries):
                self.entries.selected_index = len (self.entries) - 1
            else:
                self.entries.selected_index = self.last_index
       
        self.last_index = index
        
        # Set bind the SourceView to the SourceBuffer
        self.parent.editor.set_buffer (self.entries.selected)
        # and add focus to it
        self.parent.editor.grab_focus()
        
    def on_add_entry (self, buff):
        # We move the focus to the last selected index
        self.entries.selected = buff

        buff.connect('insert-text', self.on_insert_text)
        

    def on_insert_text (self, buff, it, text, length):
        buff.show_completion (text,
                              it,
                              self.parent.editor,
                              self.parent.plugin.pida.mainwindow)
    
    def on_remove_entry (self, entry, index):
        # If we have 0 entries then we add one
        if len (self.entries) == 0:
            self.entries.append (CulebraBuffer())
        
        
class EditWindow(gtk.EventBox, Component):
    __gsignals__ = {
        # Event called when the search-replace action is performed
        "search-replace-event": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "search-event": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "goto-line-event": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        "buffer-changed": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,)),
        "buffer-closed-event": (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    components = (
        BufferManagerListener, GotoLineComponent,
        SearchReplaceComponent, SearchComponent, ToolbarSensitivityComponent,
        
    )
    
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
        
        self.hpaned.add2(scrolledwin2)
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
            ('EditFind', gtk.STOCK_FIND, "Find...", None, "Search for text", self.edit_find),
            ('EditFindNext', gtk.STOCK_FIND, 'Find _Next', 'F3', None, self.edit_find_next),
            ('EditReplace', gtk.STOCK_FIND_AND_REPLACE, "_Replace...", '<control>h', 
                "Search for and replace text", self.edit_replace),
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
            self.entries.append (buff)
            # We only update the contents of a new buffer
            try:
                fd = open(fname)
                buff.begin_not_undoable_action()
                buff.set_text('')
                buff.set_text(fd.read())
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
        buff.save = False

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
            while blockend.forward_chars(BLOCK_SIZE):
                buf = buff.get_text(start, blockend)
                fd.write(buf)
                start = blockend.copy()
            buf = buff.get_text(start, blockend)
            fd.write(buf)
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
        self.emit ("buffer-closed-event")

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

    def edit_find(self, mi):
        self.emit("search-event")
        
    def edit_replace(self, mi):
        self.emit("search-replace-event")
            
    def edit_find_next(self, mi):
        self.get_current().search(buff.search_string, 
                                  buff.search_mark, 
                                  editor = self.editor)
    
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
