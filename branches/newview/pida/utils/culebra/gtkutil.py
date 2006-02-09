__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

# Most of this code is redudant because it's also present on 'rat' module.
import gtk

#################
# gtk.TextBuffer utility functions

def hide_on_delete(window):
    """
    Makes a window hide it self instead of getting destroyed.
    """
    
    def on_delete(wnd, *args):
        wnd.hide()
        return True
        
    return window.connect("delete-event", on_delete)


class SignalHolder:
    def __init__(self, obj, signal, cb):
        self.source = obj.connect(signal, cb)
        self.obj = obj
    
    def __del__(self):
        self.obj.disconnect(self.source)
