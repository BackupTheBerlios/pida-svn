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
import gtk
import components as binding
from constants import *

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
        
        
