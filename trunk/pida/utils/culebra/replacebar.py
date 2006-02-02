# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
import weakref

from common import ACTION_FIND_TOGGLE, ACTION_REPLACE_FORWARD, ACTION_REPLACE_ALL
from common import escape_text, unescape_text
from common import get_action, ACTION_REPLACE_TOGGLE

from bar import Bar

class ReplaceBar(Bar):
    """
    This component implements an event that validates when the selection is
    synchronized with the selected text.
    """
    def __init__(self, parent, search_bar, action_group):
        self._search_bar = weakref.ref(search_bar)
        super(ReplaceBar, self).__init__(parent, action_group)
    
    def _create_toggle_action(self, action_group):
        action = lambda name: get_action(action_group.get_action, name)
        self.toggle_find = action(ACTION_FIND_TOGGLE)
        self.replace_forward = action(ACTION_REPLACE_FORWARD)
        self.replace_all = action(ACTION_REPLACE_ALL)
        return action(ACTION_REPLACE_TOGGLE)
    
    ##############
    # Properties
    
    #############
    # search_bar
    def get_search_bar(self):
        return self._search_bar()
    
    search_bar = property(get_search_bar)
    
    ###################
    # replace_entry
    _replace_entry = None
    
    def create_replace_entry(self):
        entry = gtk.Entry()
        self.replace_completion = gtk.EntryCompletion()
        entry.set_completion(self.replace_completion)
        self.replace_model = gtk.ListStore(str)
        self.replace_completion.set_model(self.replace_model)
        self.replace_completion.set_text_column(0)
        entry.show()
        entry.connect("changed", self.on_entry_changed)
        return entry
    
    def get_replace_entry(self):
        if self._replace_entry is None:
            self._replace_entry = self.create_replace_entry()
        return self._replace_entry

    replace_entry = property(get_replace_entry)
    ###############
    # replace_text
    def get_replace_text(self):
        return self.replace_entry.get_text()
    
    replace_text = property(get_replace_text)
    
    ##############
    # widget
    def create_widget(self):
        hig_add = lambda container, widget: \
                  container.pack_start(widget, expand = False, fill = False)
        
        hbox = gtk.HBox(spacing=6)
        hbox.connect("show", self.on_show)
        hbox.connect("hide", self.on_hide)
        
        lbl = gtk.Label("Replace")
        lbl.show()
        hig_add(hbox, lbl)
        
        self.replace_entry.show()
        hig_add(hbox, self.replace_entry)
        
        btn = gtk.Button(stock=gtk.STOCK_FIND_AND_REPLACE)
        self.replace_forward.connect_proxy(btn)
        btn.show()
        hig_add(hbox, btn)
        
        btn = gtk.Button(stock=gtk.STOCK_FIND_AND_REPLACE)
        btn.set_label("Replace All")
        self.replace_all.connect_proxy(btn)
        btn.show()
        hig_add(hbox, btn)

        self.replace_forward.connect("activate", self.on_replace_curr)
        self.replace_all.connect("activate", self.on_replace_all)

        self.search_bar.widget.connect("key-release-event", self._on_key_pressed)
        
        return hbox
    
    ##################
    # Template methods

    def _bind_buffer(self, buff):
        buff.replace_component.events.register("changed", self.on_replace_changed)
        buff.replace_text = self.replace_entry.get_text()
    
    def _unbind_buffer(self, buff):
        buff.replace_component.events.unregister("changed", self.on_replace_changed)

    def on_show(self, dialog):
        self.toggle_find.set_active(True)
        self.toggle_find.set_sensitive(False)
    
    def on_hide(self, dialog):
        self.toggle_find.set_active(False)
        self.toggle_find.set_sensitive(True)
    
    def can_update_history(self):
        return self.replace_entry.get_text() in [x[0] for x in self.replace_model]
    
    def update_history(self):
        self.replace_model.append((self.replace_entry.get_text(),))
    
    def on_replace_curr(self, btn):
        if self.buffer.replace() and self.can_update_history():
            self.update_history()

        self.buffer.search()
        
    
    def on_replace_all(self, btn):
        if self.buffer.replace_all() and self.can_update_history():
            self.update_history()
        
    def on_entry_changed(self, entry):
        self.buffer.replace_text = unescape_text(entry.get_text())
    
    def on_replace_changed(self, text):
        self.replace_entry.set_text(escape_text(text))
