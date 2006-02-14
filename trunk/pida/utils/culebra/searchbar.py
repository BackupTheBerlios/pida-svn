# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
import weakref

from common import ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD, ACTION_FIND_TOGGLE
from common import escape_text, unescape_text
from rat.text import get_buffer_selection
from bar import Bar
from gtkutil import SignalHolder




class SearchBar(Bar):
    _cycle = True
    
    def __init__(self, parent, action_group):
        self.entry = gtk.Entry()
        self.search_model = gtk.ListStore(str)
        self._widget = None
        
        super(SearchBar, self).__init__(parent, action_group)

    def _create_toggle_action(self, action_group):
        self.find_forward = action_group.get_action(ACTION_FIND_FORWARD)
        self.find_backward = action_group.get_action(ACTION_FIND_BACKWARD)
        return action_group.get_action(ACTION_FIND_TOGGLE)
    
    
    def create_widget(self):

        hbox = gtk.HBox(spacing=6)
        hbox.connect("show", self.on_show)
        hbox.connect("hide", self.on_hide)
        
        lbl = gtk.Label("Search:")
        lbl.show()
        lbl.set_name("label")
        hbox.pack_start(lbl, expand = False, fill = False)
        
        entry = self.entry
        entry.set_name("entry")
        entry.connect("changed", self.on_entry_changed)
        entry.connect("focus", self.on_entry_focus)
        entry.connect("activate", self.on_entry_activate)
        self.search_completion = gtk.EntryCompletion()
        entry.set_completion(self.search_completion)
        self.search_completion.set_model(self.search_model)
        self.search_completion.set_text_column(0)
        entry.show()
        entry.set_activates_default(True)
        hbox.pack_start(entry, expand=False, fill=False)
        

        # Find backwards
        btn_back = gtk.Button(stock=gtk.STOCK_GO_BACK)
        btn_back.show()
        btn_back.set_name("backward")
        self.btn_backward = btn_back
        self.find_backward.connect_proxy(btn_back)
        hbox.pack_start(btn_back, expand=False, fill=False)

        # Find forward
        btn_forward = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        btn_forward.show()
        btn_forward.set_name("forward")
        self.btn_forward = btn_forward
        self.find_forward.connect_proxy(btn_forward)
        
        hbox.pack_start(btn_forward, expand=False, fill=False)
        
        return hbox
        

    
    def _bind_buffer(self, buff):
        search = buff.search_component
        search.events.register("changed", self.on_search_changed)
        search.events.register("no-more-entries", self.on_no_entries)
        search.search_text = self.entry.get_text()

        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
    
    def _unbind_buffer(self, buff):
        search = buff.search_component
        search.events.unregister("changed", self.on_search_changed)
        search.events.unregister("no-more-entries", self.on_no_entries)
    
    def on_no_entries(self, find_forward):
        if not self._cycle:
            return

        buff = self.buffer
        bounds = self.buffer.get_selection_bounds()
        
        if len(bounds) == 0:
            return
            
        start_iter = bounds[0]

        if find_forward:
            next_iter = self.buffer.get_start_iter()
        else:
            next_iter = self.buffer.get_end_iter()
            
        self.buffer.place_cursor(next_iter)
        
        if self.buffer.search(find_forward, trigger=False):
            # If we find an entry now
            next_iter = buff.get_selection_bounds()[0]
            # And the iterator is not the same
            if not next_iter.equal(start_iter):
                # Focus the carret
                self.get_parent().focus_carret()
        
        else:
            # Undo the selection
            buff.select_range(*bounds)

    def on_entry_activate(self, entry, *args):
        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
        self.btn_forward.activate()

    def on_show(self, dialog):
        buff = self.buffer
        
        selected_text = get_buffer_selection(buff)
        if selected_text != "":
            # There's some selected text, copy it to the search entry
            self.entry.set_text(selected_text)
        else:
            # Select some text on the buffer
            self.find_forward.activate()
            
        # Select text entry and focus on it
        self.entry.select_region(0, -1)
        self.entry.grab_focus()

        buff.search_highlight = True

    
    def on_hide(self, dialog):
        # Hide search the marks
        self.buffer.search_highlight = False
    
    def on_entry_focus(self, entry, *args):
        # Select all
        entry.select_region(0, -1)

    def on_search_changed(self, text):
        self.entry.set_text(escape_text(text))

    def on_entry_changed(self, entry):

        txt = entry.get_text()
        
        is_sensitive = txt != ""
        self.find_forward.set_sensitive(is_sensitive)
        self.find_backward.set_sensitive(is_sensitive)
        
        if txt != escape_text(txt):
            # Escaped text is different from provided text, which means
            # the user inserted a \n or a \t, update the text and try again
            entry.set_text(escape_text(txt))
            return
        
        # XXX: the only reason this is here is because the action group
        # XXX: is set when the buffer is None, when the action group is set
        # XXX: it calls on_entry_changed
        if self.buffer is not None:
            self.buffer.search_text = unescape_text(txt)
    
    def set_action_group(self, action_group):
        super(SearchBar, self).set_action_group(action_group)
        self.on_entry_changed(self.entry)
        
        if action_group is None:
            self.find_forward_source = None
            self.find_backward_source = None
            return
            
        holder = SignalHolder(self.find_forward, "activate", self.on_find_forward)
        self.find_forward_source = holder
        
        find_backward = action_group.get_action(ACTION_FIND_BACKWARD)
        holder = SignalHolder(self.find_backward, "activate", self.on_find_backward)
        self.find_backward_source = holder
        

    def on_find_forward(self, action):
        self.get_parent().find(True)
    
    def on_find_backward(self, action):
        self.get_parent().find(False)

