# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
import weakref

from common import ACTION_FIND_TOGGLE, ACTION_REPLACE_FORWARD, ACTION_REPLACE_ALL
from common import escape_text, unescape_text
from common import get_action, ACTION_REPLACE_TOGGLE
from gtkutil import subscribe_proxy, signal_holder
from bar import Bar
import interfaces
import core

class ReplaceBar(Bar):
    """
    This component implements an event that validates when the selection is
    synchronized with the selected text.
    """
    
    search_bar = core.Depends(interfaces.ISearchBar)
    replace = core.Depends(interfaces.IReplace)
    search = core.Depends(interfaces.ISearch)
    carret = core.Depends(interfaces.ICarretController)
    
    def __init__(self):
        btn = gtk.Button(stock=gtk.STOCK_FIND_AND_REPLACE)
        self.btn_replace_forward = btn
        btn = gtk.Button(stock=gtk.STOCK_FIND_AND_REPLACE)
        btn.set_label("Replace All")
        self.btn_replace_all = btn
    
    def _bind(self, service_provider):
        cb = self.on_replace_changed
        self.evt = self.replace.register_event("text-changed", cb)
    
    def _create_toggle_action(self, action_group):
        action = lambda name: get_action(action_group.get_action, name)
        return action(ACTION_REPLACE_TOGGLE)
    
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
        
        btn = self.btn_replace_forward
        btn.show()
        hig_add(hbox, btn)
        
        btn = self.btn_replace_all
        btn.show()
        hig_add(hbox, btn)

        self.search_bar.widget.connect("key-release-event", self._on_key_pressed)
        return hbox
    
    
    def set_action_group(self, action_group):
        super(ReplaceBar, self).set_action_group(action_group)
        # This is a little gimmnick to make it not throw an exception
        # Since the holders return None when the first argument is
        # None.
        if action_group is None:
            get_action = lambda name: None
        else:
            get_action = lambda name: action_group.get_action(name)
        
        replace_forward = get_action(ACTION_REPLACE_FORWARD)
        replace_all = get_action(ACTION_REPLACE_ALL)
        self.toggle_find = get_action(ACTION_FIND_TOGGLE)
        self.signal_1 = signal_holder(replace_forward, "activate", self.on_replace_curr)
        self.signal_2 = signal_holder(replace_all, "activate", self.on_replace_all)
        
        sbs = subscribe_proxy(replace_forward, self.btn_replace_forward)
        self.replace_forward_src = sbs
        
        sbs = subscribe_proxy(replace_all, self.btn_replace_all)
        self.replace_all_src = sbs
        

    
    ##################
    # Template methods
    

    def _bind_buffer(self, buff):
        buff.replace_component.events.register("changed", self.on_replace_changed)
        buff.replace_text = self.replace_entry.get_text()
    
    def _unbind_buffer(self, buff):
        buff.replace_component.events.unregister("changed", self.on_replace_changed)

    def on_show(self, dialog):
        if self.toggle_find is None:
            return
        self.toggle_find.set_active(True)
        self.toggle_find.set_sensitive(False)
    
    def on_hide(self, dialog):
        if self.toggle_find is None:
            return
        self.toggle_find.set_active(False)
        self.toggle_find.set_sensitive(True)
    
    def can_update_history(self):
        return self.replace_entry.get_text() in [x[0] for x in self.replace_model]
    
    def update_history(self):
        self.replace_model.append((self.replace_entry.get_text(),))
    
    def on_replace_curr(self, btn):
        if self.replace.replace() and self.can_update_history():
            self.update_history()

        self.search.search()
        self.carret.focus_carret()
    
    def on_replace_all(self, btn):
        if self.replace.replace_all() and self.can_update_history():
            self.update_history()
            self.get_parent().focus_carret()
        
    def on_entry_changed(self, entry):
        self.replace.set_text(unescape_text(entry.get_text()))
    
    def on_replace_changed(self, replace):
        text = replace.get_text()
        self.replace_entry.set_text(escape_text(text))

def register_services(service_provider):
    service_provider.register_factory(ReplaceBar, interfaces.IReplaceBar)
