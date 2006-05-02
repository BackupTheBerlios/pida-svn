# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

class SaveLinker:
    """Makes the buffer's modified state affect an actions sensitivity"""
    def __init__(self, buff, action):
        self.buff = buff
        
        def on_modified(buff):
            action.set_sensitive(buff.get_modified())
        
        self.source = buff.connect("modified-changed", on_modified)
        on_modified(buff)
    
    
    
    def __del__(self):
        self.buff.disconnect(self.source)

