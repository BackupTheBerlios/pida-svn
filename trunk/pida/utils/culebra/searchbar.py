# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
import weakref

from common import ACTION_FIND_FORWARD, ACTION_FIND_BACKWARD, ACTION_FIND_TOGGLE
from common import escape_text, unescape_text
from rat.text import get_buffer_selection, search_iterator
from bar import Bar
from gtkutil import signal_holder, subscribe_proxy

def has_search_entries(buff):
    """Returns if a certain buffer contains or not a search string"""
    entries = search_iterator(buff, buff.search_text, start_in_cursor=False)
    for bounds in entries:
        return True
        
    return False


# TODO: there's a problem when edit.main() is called with BufferSubscription
# refs
class BufferSubscription:
    def __init__(self, buff, obj):
        search = buff.search_component
        search.events.register("changed", obj.on_search_changed)
        search.events.register("no-more-entries", obj.on_no_entries)
        search.search_text = obj.entry.get_text()
        self.buff = weakref.ref(buff)
        self.obj = weakref.ref(obj)

    def __del__(self):
        search = self.buff().search_component
        search.events.unregister("changed", self.obj().on_search_changed)
        search.events.unregister("no-more-entries", self.obj().on_no_entries)


class SearchBar(Bar):
    _cycle = True
    _buffer_subscription_factory = BufferSubscription
    
    def __init__(self, parent, action_group):
        self._widget = None
        self._signals = []
        self.entry = self.create_entry()
        self.forward_button = self.create_forward_button()
        self.backward_button = self.create_backward_button()
        
        super(SearchBar, self).__init__(parent, action_group)

    def _create_toggle_action(self, action_group):
        self.find_forward = action_group.get_action(ACTION_FIND_FORWARD)
        self.find_backward = action_group.get_action(ACTION_FIND_BACKWARD)
        return action_group.get_action(ACTION_FIND_TOGGLE)
    
    def _connect(self, *args, **kwargs):
        self._signals.append(signal_holder(*args, **kwargs))
    
    def create_entry(self):
        entry = gtk.Entry()
        entry.set_name("entry")
        # TODO: do not referentiate self
        self._connect(entry, "changed", self.on_entry_changed)
#        self._connect(entry, "changed", self.on_entry_changed)
        self._connect(entry, "focus", self.on_entry_focus)
        self._connect(entry, "activate", self.on_entry_activate)
        
        entry.show()
        entry.set_activates_default(True)
        return entry
    
    def create_forward_button(self):
        btn_forward = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        btn_forward.show()
        btn_forward.set_name("forward")
        return btn_forward


    def create_backward_button(self):    
        btn_back = gtk.Button(stock=gtk.STOCK_GO_BACK)
        btn_back.show()
        btn_back.set_name("backward")
        return btn_back
        
    def create_widget(self):

        hbox = gtk.HBox(spacing=6)
        self._connect(hbox, "show", self.on_show)
        self._connect(hbox, "hide", self.on_hide)
        
        lbl = gtk.Label("Search:")
        lbl.show()
        lbl.set_name("label")
        hbox.pack_start(lbl, expand=False, fill=False)
        
        # Text Entry
        assert self.entry is not None
        hbox.pack_start(self.entry, expand=False, fill=False)

        # Find backward
        btn_back = self.backward_button
        hbox.pack_start(btn_back, expand=False, fill=False)

        # Find forward
        btn_forward = self.forward_button
        hbox.pack_start(btn_forward, expand=False, fill=False)
        
        return hbox
    

    def _bind_buffer(self, buff):
        search = buff.search_component
        search.events.register("changed", self.on_search_changed)
        search.events.register("no-more-entries", self.on_no_entries)
        search.search_text = self.entry.get_text()

    
    def _unbind_buffer(self, buff):
        search = buff.search_component
        search.events.unregister("changed", self.on_search_changed)
        search.events.unregister("no-more-entries", self.on_no_entries)
    
    def on_no_entries(self, find_forward):
        if not self._cycle:
            return

        # We have to cycle we need to:
        # 1. get the orientation of where we're searching
        # 2. find out if there are no entries at all
        # 3. move to the top/bottom and grab the next one
        buff = self.buffer
        
        if not has_search_entries(buff):
            return

        if find_forward:
            next_iter = self.buffer.get_start_iter()
        else:
            next_iter = self.buffer.get_end_iter()

        self.buffer.place_cursor(next_iter)
        
        if find_forward:
            self.forward_button.clicked()
        else:
            self.backward_button.clicked()
                    

    def on_entry_activate(self, entry, *args):
        self.forward_button.clicked()

    def on_show(self, dialog):
        buff = self.buffer
        
        selected_text = get_buffer_selection(buff)
        if selected_text != "":
            # There's some selected text, copy it to the search entry
            self.entry.set_text(selected_text)
        #else:
            # Select some text on the buffer
            #self.forward_button.clicked()
            
        # Select text entry and focus on it
        self.entry.select_region(0, -1)
        self.entry.grab_focus()
        
        if not buff.search_highlight:
            buff.search_highlight = True

    
    def on_hide(self, dialog):
        # Hide search the marks
        if self.buffer.search_highlight:
            self.buffer.search_highlight = False
    
    def on_entry_focus(self, entry, *args):
        # Select all
        entry.select_region(0, -1)

    def on_search_changed(self, text):
        self.entry.set_text(escape_text(text))

    def on_entry_changed(self, entry):

        txt = entry.get_text()
        
        is_sensitive = txt != ""
        if self.find_forward is None:
            self.forward_button.set_sensitive(is_sensitive)
            self.backward_button.set_sensitive(is_sensitive)
        else:
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
        
        # This is a little gimmnick to make it not throw an exception
        # Since the holders return None when the first argument is
        # None.
        if action_group is None:
            get_action = lambda name: None
        else:
            get_action = lambda name: action_group.get_action(name)
        
        # Update references
        self.find_forward = get_action(ACTION_FIND_FORWARD)
        self.find_backward = get_action(ACTION_FIND_BACKWARD)
        
        # Update signal subscription
        hld = signal_holder(self.find_forward, "activate", self.on_find_forward)
        self.find_forward_source = hld

        act = self.find_backward
        hld = signal_holder(act, "activate", self.on_find_backward)
        self.find_backward_source = hld
        
        # Update action proxy subscription
        fw = subscribe_proxy(self.find_forward, self.forward_button)
        self.forward_button_source = fw

        bw = subscribe_proxy(self.find_backward, self.backward_button)
        self.backward_button_source = bw

        # Propagate entry state
        self.on_entry_changed(self.entry)
        
        

    def on_find_forward(self, action):
        self.get_parent().find(True)
    
    def on_find_backward(self, action):
        self.get_parent().find(False)

    def destroy(self):
        self._signals = []
        

