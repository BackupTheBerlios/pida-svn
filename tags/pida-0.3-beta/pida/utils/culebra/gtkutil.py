__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

# Most of this code is redudant because it's also present on 'rat' module.
import gtk

#################
# gtk.TextBuffer utility functions
def get_buffer_selection(buffer):
    """Returns the selected text, when nothing is selected it returns the empty
    string."""
    bounds = buffer.get_selection_bounds()
    if len(bounds) == 0:
        return ""
    else:
        return buffer.get_slice(*bounds)

class SearchIterator:
    def __init__(self, text_buffer, search_text, find_forward=True, start_in_cursor=True):
        self.search_text = search_text
        self.text_buffer = text_buffer
        self.find_forward = find_forward
        
        
        if start_in_cursor:
            bounds = text_buffer.get_selection_bounds()
            if len(bounds) == 0:
                self.next_iter = text_buffer.get_iter_at_mark(text_buffer.get_insert())
            else:
                self.next_iter = find_forward and bounds[1] or bounds[0]
        else:
            if find_forward:
                self.next_iter = text_buffer.get_start_iter()
            else:
                self.next_iter = text_buffer.get_end_iter()
        
        
        
    def next(self):
        if self.next_iter is None:
            raise StopIteration
        
        find_forward = self.find_forward
        
        if find_forward:
            search = self.next_iter.forward_search
        else:
            search = self.next_iter.backward_search
            
        bounds = search(self.search_text, gtk.TEXT_SEARCH_TEXT_ONLY, limit=None)
        
        if bounds is None:
            self.next_iter = None
            raise StopIteration
        
        if find_forward:
            self.next_iter = bounds[1]
        else:
            self.next_iter = bounds[0]
        
        return bounds
    
    def __iter__(self):
        return self
        
def search_iterator(text_buffer, search_text, find_forward = True, start_in_cursor = True):
    """
    This function implements an iterator for searching a gtk.TextBuffer for
    a certain string.
    
    It supports forward and backwards search.
    
    It also supports finding from the start or from where the cursor is located.
    """

    if start_in_cursor:
        bounds = text_buffer.get_selection_bounds()
        if len(bounds) == 0:
            text_iter = text_buffer.get_iter_at_mark(text_buffer.get_insert())
        else:
            text_iter = find_forward and bounds[1] or bounds[0]
    else:
        if find_forward:
            text_iter = text_buffer.get_start_iter()
        else:
            text_iter = text_buffer.get_end_iter()
    
    bounds = 1
    while bounds is not None:
        if find_forward:
            search = text_iter.forward_search
            
        else:
            search = text_iter.backward_search
            
        bounds = search(search_text, gtk.TEXT_SEARCH_TEXT_ONLY, limit=None)
        
        if bounds is None:
            break
            
        yield bounds
        
        if find_forward:
            text_iter = bounds[1]
        else:
            text_iter = bounds[0]

search_iterator = SearchIterator

def hide_on_delete(window):
    """
    Makes a window hide it self instead of getting destroyed.
    """
    
    def on_delete(wnd, *args):
        wnd.hide()
        return True
        
    return window.connect("delete-event", on_delete)


