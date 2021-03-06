﻿# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
import weakref

from gtkutil import *
from common import *

class ReplaceBar(ChildObject):
    """
    This component implements an event that validates when the selection is
    synchronized with the selected text.
    """
    def __init__(self, parent, search_bar, toggle_find, toggle_replace, replace_forward, replace_all):
        super(ReplaceBar, self).__init__(parent)
        self._search_bar = weakref.ref(search_bar)

        self.toggle_find = toggle_find
        self.toggle_replace = toggle_replace
        self.replace_forward = replace_forward
        self.replace_all = replace_all
        # XXX: this is only here because there's one replace_bar per buffer
        # TODO: make it non dependant and make it 
        #self.bind(self.get_buffer())
        self.toggle_replace.connect("activate", self.on_replace_toggled)    
    
    ##############
    # Properties
    
    #############
    # search_bar
    def get_search_bar(self):
        return self._search_bar()
    
    search_bar = property(get_search_bar)
    
    #############
    # buffer
    _buffer = None
    
    def set_buffer(self, buff):
        if self._buffer is not None:
            self.unbind(self.buffer)
            
        self._buffer = weakref.ref(buff)
        self.bind(buff)
    
    def get_buffer(self):
        if self._buffer is None:
            return None
        return self._buffer()
    
    buffer = property(get_buffer, set_buffer)
    
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
        
        hbox = gtk.HBox(spacing = 6)
        hbox.connect("key-release-event", self.on_key_pressed)
        hbox.connect("show", self.on_show)
        hbox.connect("hide", self.on_hide)
        
        lbl = gtk.Label("Replace")
        lbl.show()
        hig_add(hbox, lbl)
        
        self.replace_entry.show()
        hig_add(hbox, self.replace_entry)
        
        btn = gtk.Button(stock = gtk.STOCK_FIND_AND_REPLACE)
        self.replace_forward.connect_proxy(btn)
        btn.show()
        hig_add(hbox, btn)
        
        btn = gtk.Button(stock = gtk.STOCK_FIND_AND_REPLACE)
        btn.set_label("Replace All")
        self.replace_all.connect_proxy(btn)
        btn.show()
        hig_add(hbox, btn)

        self.replace_forward.connect("activate", self.on_replace_curr)
        self.replace_all.connect("activate", self.on_replace_all)

        self.search_bar.widget.connect("key-release-event", self.on_key_pressed)
        
        return hbox
    
    _widget = None
    
    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
        return self._widget
    
    widget = property(get_widget)
    
    ##################
    # Methods

    def bind(self, buff):
        buff.replace_component.events.register("changed", self.on_replace_changed)
        buff.replace_text = self.replace_entry.get_text()
    
    def unbind(self, buff):
        buff.replace_component.events.unregister("changed", self.on_replace_changed)

    def on_show(self, dialog):
        self.toggle_find.set_active(True)
        self.toggle_find.set_sensitive(False)
    
    def on_hide(self, dialog):
        self.toggle_find.set_active(False)
        self.toggle_find.set_sensitive(True)
    
    def on_key_pressed(self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.toggle_replace.set_active(False)

    def on_replace_toggled(self, action):
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()
        
    def on_replace_curr(self, btn):
        if not self.replace_entry.get_text() in [x[0] for x in self.replace_model]:
            self.replace_model.append((self.replace_entry.get_text(),))
        self.buffer.replace()
        self.buffer.search()
    
    def on_replace_all(self, btn):
        if not self.replace_entry.get_text() in [x[0] for x in self.replace_model]:
            self.replace_model.append((self.replace_entry.get_text(),))
        self.buffer.replace_all()
        
    def on_entry_changed(self, entry):
        self.buffer.replace_text = unescape_text(entry.get_text())
    
    def on_replace_changed(self, text):
        self.replace_entry.set_text(escape_text(text))