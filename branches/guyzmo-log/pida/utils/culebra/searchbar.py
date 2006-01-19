# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
from common import *
from gtkutil import *


class SearchBar(ChildObject):
    def __init__(self, parent, action_group):
        super(SearchBar, self).__init__(parent)

        self.find_forward = action_group.get_action(ACTION_FIND_FORWARD)
        self.find_backwards = action_group.get_action(ACTION_FIND_BACKWARD)
        self.show_find = action_group.get_action(ACTION_FIND_TOGGLE)
        self._widget = None
        self.show_find.connect("toggled", self.on_toggle_find)
    
    def create_widget(self):

        hbox = gtk.HBox(spacing=6)
        hbox.connect("show", self.on_show)
        hbox.connect("hide", self.on_hide)
        hbox.connect("key-release-event", self.on_key_pressed)
        
        lbl = gtk.Label("Search:")
        lbl.show()
        hbox.pack_start(lbl, expand = False, fill = False)
        
        entry = gtk.Entry()
        entry.connect("changed", self.on_entry_changed)
        entry.connect("focus", self.on_entry_focus)
        entry.connect("activate", self.on_entry_activate)
        self.search_completion = gtk.EntryCompletion()
        entry.set_completion(self.search_completion)
        self.search_model = gtk.ListStore(str)
        self.search_completion.set_model(self.search_model)
        self.search_completion.set_text_column(0)
        entry.show()
        entry.set_activates_default(True)
        self.entry = entry
        hbox.pack_start(entry, expand=False, fill=False)
        

        # Find backwards
        btn_back = gtk.Button(stock=gtk.STOCK_GO_BACK)
        btn_back.show()
        self.btn_backward = btn_back
        self.find_backwards.connect_proxy(btn_back)
        hbox.pack_start(btn_back, expand=False, fill=False)

        # Find forward
        btn_forward = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        btn_forward.show()
        self.btn_forward = btn_forward
        self.find_forward.connect_proxy(btn_forward)
        
        hbox.pack_start(btn_forward, expand=False, fill=False)
        
        #-----
        self.bind(self.get_parent().get_buffer())

        return hbox
        
    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
        
        return self._widget
    
    widget = property(get_widget)
    
    def bind(self, buff):
        search = buff.search_component
        search.events.register("changed", self.on_search_changed)
        search.events.register("no-more-entries", self.on_no_entries)
        search.search_text = self.entry.get_text()

        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
    
    def unbind(self, buff):
        buff.search.events.unregister("changed", self.on_search_changed)
        buff.search.events.unregister("no-more-entries", self.on_no_entries)
        buff.search_highlight = False
    
    def on_no_entries(self, find_forward):
        return
        #XXX: fix this, it should go to top
        if find_forward:
            self.btn_backward.grab_focus()
        else:
            self.btn_forward.grab_focus()

    def on_clicked(self, btn):
        buff = self.get_parent().get_buffer()
        buff.search_text = self.entry.get_text()
        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
    
    def on_entry_activate(self, entry, *args):
        if not self.entry.get_text() in [x[0] for x in self.search_model]:
            self.search_model.append((self.entry.get_text(),))
        self.btn_forward.activate()

    def on_show(self, dialog):
        buff = self.get_parent().get_buffer()
        
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
        self.get_parent().get_buffer().search_highlight = False
    
    def on_key_pressed(self, search_text, event):
        #When the ESCAPE key is pressed deactivate the Find action 
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.show_find.set_active(False)
    
    def on_toggle_find(self, action):
        #When the action is active show the bar else it's hidden
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()

    def on_entry_focus(self, entry, *args):
        # Select all
        entry.select_region(0, -1)

    def on_search_changed(self, text):
        self.entry.set_text(escape_text(text))

    def on_entry_changed(self, entry):
        txt = entry.get_text()
        if txt != escape_text(txt):
            # Escaped text is different from provided text, which means
            # the user inserted a \n or a \t, update the text and try again
            entry.set_text(escape_text(txt))
            return

        is_sensitive = txt != ""
        self.find_forward.set_sensitive(is_sensitive)
        self.find_backwards.set_sensitive(is_sensitive)
        self.get_parent().get_buffer().search_text = unescape_text(txt)
    
