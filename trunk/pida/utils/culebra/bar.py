# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

from common import *

class Bar(ChildObject):
    def __init__(self, parent, action_group):
        super(Bar, self).__init__(parent)
        self.bind_action_group(action_group)
    
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
    
    ############
    # Widget

    _widget = None
    
    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
            self._widget.connect("key-release-event", self.on_key_pressed)
        return self._widget
    
    widget = property(get_widget)
    
    ##########
    # Methods
    def bind_action_group(self, action_group):
        self.toggle_action = self._create_toggle_action(action_group)
        src = self.toggle_action.connect("toggled", self.on_action_toggled)
        self.toggle_source = src
        
    def unbind_action_group(self):
        self.toggle_action.disconnect("toggled", self.toggle_source)
        
    def on_action_toggled(self, action):
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()
        
    def on_key_pressed(self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.toggle_action.set_active(False)


       
