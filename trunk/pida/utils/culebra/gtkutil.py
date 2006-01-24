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

def line_iterator(buff, start_iter, end_iter):
    begin_line = start_iter.get_line()
    end_line = end_iter.get_line()
    assert begin_line <= end_line
    for line_num in range(begin_line, end_line+1):
        yield buff.get_iter_at_line(line_num)

def selected_line_iterator(buff):
    bounds = buff.get_selection_bounds()
    if len(bounds) == 0:
        return
    last_iter = bounds[1]
    
    for start_iter in line_iterator(buff, *bounds):
        # Skip empty lines
        if start_iter.equal(last_iter) or start_iter.ends_line():
            continue
        yield start_iter

def indent_selected(buff, indent):
    """
    Indents selected text of a gtk.TextBuffer
    """
    
    bounds = buff.get_selection_bounds()
    if len(bounds) == 0:
        return False
    
    move_home = bounds[0].starts_line()
    
    for start_iter in selected_line_iterator(buff):
        buff.insert(start_iter, indent)
    
    if move_home:
        start_iter, end_iter = buff.get_selection_bounds()
        start_iter.set_line_offset(0)
        buff.select_range(end_iter, start_iter)

    return True
    
    
def unindent_selected(buff, indent, use_subset=True):
    """
    Unindents selected text of a gtk.TextBuffer 
    """
    for start_iter in selected_line_iterator(buff):
        # Get the iterator of the end of the text
        end_iter = start_iter.copy()
        end_iter.forward_to_line_end()
        total = len(indent)
        
        # Now get the selected text
        text = buff.get_text(start_iter, end_iter)
        
        # Check if the text starts with indent:
        if text.startswith(indent):
            count = len(indent)
            # Delete 'count' characters
            end_iter = start_iter.copy()
            end_iter.forward_chars(count)
            buff.delete(start_iter, end_iter)

        elif use_subset:
            for count in range(1, len(indent)):
                if text.startswith(indent[:-count]):
                    # Delete 'count' characters
                    offset = len(indent) - count
                    end_iter = start_iter.copy()
                    end_iter.forward_chars(offset)
                    buff.delete(start_iter, end_iter)
                    break

def _on_key_press(view, event):
    keyname = gtk.gdk.keyval_name(event.keyval)
    buff = view.get_buffer()
    
    if view.get_insert_spaces_instead_of_tabs():
        tab = " " * view.get_tabs_width()
    else:
        tab = "\t"
    if event.state & gtk.gdk.SHIFT_MASK and keyname == "ISO_Left_Tab":
        unindent_selected(buff, tab)
        return True
        
    elif event.keyval == gtk.keysyms.Tab:
        indent_selected(buff, tab)
        return True



def make_source_view_indentable(source_view):
    # TODO: make the selection carret move to the end of the selection
    # and not the start
    return source_view.connect("key-press-event", _on_key_press)

def hide_on_delete(window):
    """
    Makes a window hide it self instead of getting destroyed.
    """
    
    def on_delete(wnd, *args):
        wnd.hide()
        return True
        
    return window.connect("delete-event", on_delete)


