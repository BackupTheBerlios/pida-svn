# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

from common import *
from gtkutil import SignalHolder

class Bar(ChildObject):
    def __init__(self, parent, action_group):
        super(Bar, self).__init__(parent)
        self.set_action_group(action_group)
    
    #############
    # buffer
    _buffer = None
    
    def set_buffer(self, buff):
        old_buffer = self.buffer
        if old_buffer is not None:
            self._unbind_buffer(old_buffer)
        
        if buff is None:
            self._buffer = None
        else:
            self._buffer = weakref.ref(buff)
            self._bind_buffer(buff)
    
    def get_buffer(self):
        if self._buffer is None:
            return None
        return self._buffer()
    
    buffer = property(get_buffer, set_buffer)
    
    ############
    # Widget

    _widget = None
    
    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
            self._widget.connect("key-release-event", self._on_key_pressed)
        return self._widget
    
    widget = property(get_widget)
    
    ##########
    # Methods
    def set_action_group(self, action_group):
        if action_group is None:
            self.toggle_source = None
            return
        
        self.toggle_action = self._create_toggle_action(action_group)
        self.toggle_action.set_active(self.widget.get_property("visible"))
        
        src = SignalHolder(self.toggle_action, "toggled", self._on_action_toggled)
        self.toggle_source = src
    
    def _on_action_toggled(self, action):
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()
        
    def _on_key_pressed(self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.toggle_action.set_active(False)


       
