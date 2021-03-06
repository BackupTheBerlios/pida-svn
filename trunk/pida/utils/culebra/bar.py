# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

from common import *
from gtkutil import signal_holder
import core

def _activate_action(widget, action):
    action.set_active(True)

def _deactivate_action(widget, action):
    action.set_active(False)

def _toggle_visibility(action, widget):
    if action.get_active():
        widget.show()
    else:
        widget.hide()
    

class VisibilitySync:

    def __init__(self, widget, toggle_action, apply_now=True):

        self._activate = signal_holder(
            widget,
            "show",
            _activate_action,
            userdata=toggle_action
        )
        
        self._deactivate = signal_holder(
            widget,
            "hide",
            _deactivate_action,
            userdata=toggle_action
        )
        
        self._toggle_visible = signal_holder(
            toggle_action,
            "toggled",
            _toggle_visibility,
            userdata=widget
        )
        
        # Take effect now
        visible = widget.get_property("visible")
        if apply_now and visible != toggle_action.get_active():
            toggle_action.set_active(visible)
    

class Bar(core.BaseService):
    toggle_action = None
    
    ############
    # Widget

    _widget = None
    
    def get_widget(self):
        if self._widget is None:
            self._widget = self.create_widget()
            self._widget.connect("key-release-event", self._on_key_pressed)
            self.__update_visibility_sync()
            
        return self._widget
    
    widget = property(get_widget)
    
    def __update_visibility_sync(self):
        if self._widget is not None and self.toggle_action is not None:
            self.__visibility_sync = VisibilitySync(self._widget, self.toggle_action)
        else:
            self.__visibility_sync = None
    
    ##########
    # Methods
    def set_action_group(self, action_group):
        if action_group is None:
            self.toggle_source = None
            return
        
        self.toggle_action = self._create_toggle_action(action_group)
        self.__update_visibility_sync()

    
    def _on_action_toggled(self, action):
        if action.get_active():
            self.widget.show()
        else:
            self.widget.hide()
        
    def _on_key_pressed(self, search_text, event):
        global KEY_ESCAPE
        
        if event.keyval == KEY_ESCAPE:
            self.toggle_action.set_active(False)

    

       
