# -*- coding: utf-8 -*-
# Copyright 2005, Tiago Cogumbreiro <cogumbreiro@users.sf.net>
# $Id: edit.py 589 2005-10-14 00:14:56Z cogumbreiro $
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
import components as binding
import gtk
from constants import *

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
        self.search_completion = gtk.EntryCompletion()
        entry.set_completion(self.search_completion)
        try:
            self.search_model = self.parent.search_model
        except:
            self.search_model = gtk.ListStore(str)
            self.parent.search_model = self.search_model
        self.search_completion.set_model(self.search_model)
        self.search_completion.set_text_column(0)
        entry.show ()
        entry.set_activates_default(True)
        self.entry = entry
        hbox.pack_start (entry, expand = False, fill = False)

        # Find backwards
        btn_back = gtk.Button (stock = gtk.STOCK_GO_BACK)
        btn_back.show ()
        self.btn_backward = btn_back
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
        buff.search.events.register ("no-more-entries", self.on_no_entries)
        buff.search.search_text = self.entry.get_text ()
        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
        buff.search.enable()
    
    def unbind (self, buff):
        buff.search.events.unregister ("changed", self.on_search_changed)
        buff.search.events.unregister ("no-more-entries", self.on_no_entries)
        buff.search.disable()
    
    def on_no_entries (self, find_forward):
        if find_forward:
            self.btn_backward.grab_focus()
        else:
            self.btn_forward.grab_focus()

    def on_entry_changed (self, entry):
        is_sensitive = entry.get_text () != ""
        self.find_forward.set_sensitive (is_sensitive)
        self.find_backward.set_sensitive (is_sensitive)
        self.parent.get_current().search.search_text = entry.get_text ()
    
    def on_clicked (self, btn):
        buff = self.parent.get_current ()
        buff.search_text = self.entry.get_text ()
        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
    
    def on_entry_activate (self, entry, *args):
        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
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
            self.entry.set_text("")
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