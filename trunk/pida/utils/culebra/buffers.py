# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtk
import gobject
import interfaces
import tempfile
import os
import gtkutil
import weakref
import core
from interfaces import ORIENTATION_FORWARD, ORIENTATION_BACKWARD

try:
    from svbase import BaseBuffer
except ImportError:
    from tvbase import BaseBuffer
    
from events import EventsDispatcher
from rat.text import search_iterator, get_buffer_selection
from common import ChildObject

_VOID_VOID = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())

class EventProvider(gobject.GObject):
    __implements__ = interfaces.IEventProvider,
    
    def register_event(self, event_name, callback):
        return gtkutil.SignalHolder(self, event_name, callback)

class SafeFileWrite:
    """This class enables the user to safely write the contents to a file and
    if something wrong happens the original file will not be damaged. It writes
    the contents in a temporary file and when the file descriptor is closed the
    contents are transfered to the real filename."""
    
    def __init__(self, filename):
        self.filename = filename
        basedir = os.path.dirname(filename)
        # must be in the same directory so that renaming works
        fd, self.tmp_filename = tempfile.mkstemp(dir=basedir)
        os.close(fd)
        self.fd = open(self.tmp_filename, "w")
        
    def __getattr__(self, attr):
        return getattr(self.fd, attr)
    
    def close(self):
        self.fd.close()
        
        try:
            os.unlink(self.filename)
        except OSError:
            pass
        os.rename(self.tmp_filename, self.filename)
    
    def abort(self):
        """Abort is used to cancel the changes made and remove the temporary
        file. The original filename will not be altered."""
        self.fd.close()
        try:
            os.unlink(self.tmp_filename)
        except OSError:
            pass

#####################
class OnSearchTextChanged(ChildObject):
    
    def __call__(self, search):
        highlight = self.get_parent()
        
        if highlight.get_highlight():
            highlight.update_highlight()
            
class OnTextBufferChanged(ChildObject):
    def __call__(self, buff):
        assert self.get_parent().get_highlight()
        self.get_parent().update_highlight()
        
class _HighlightSearch(core.BaseService):
    """The parent should be a 'TextBuffer' like object"""
    buffer = core.Depends("buffer")
    search = core.Depends(interfaces.ISearch)
    
    def _bind(self, service_provider):
        
        self.search_tag = self.buffer.create_tag(
            "search_markers",
            background="yellow",
            foreground="black",
        )

        self.on_search_changed = OnSearchTextChanged(self)
        self.hld = gtkutil.signal_holder(self.search, "text-changed",
                                         self.on_search_changed)
        self.on_txt_changed = OnTextBufferChanged(self)
    
    def clear_highlight(self):
        self.buffer.remove_tag(
            self.search_tag,
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter()
        )

    def update_highlight(self):
        # Remove old highlight
        self.clear_highlight()
        
        if self.search.get_text() == "":
            # Nothing to highlight 
            return
        
        # Apply tag to found entries
        bounds = search_iterator(self.buffer, self.search.get_text(), start_in_cursor=False)
        apply_tag = self.buffer.apply_tag
        search_tag = self.search_tag
        
        # These are optimizations for:
        #for start, end in bounds:
        #     apply_tag(self.search_tag, start, end)

        # Use local pointers instead of dots
        # use the 'map' function
        apply_tag_cycle = lambda bounds: apply_tag(search_tag, bounds[0], bounds[1])
        map(apply_tag_cycle, bounds)

        
    src = None
    def disable_highlight(self):
        # No longer listen for the changed buffer
        self.src = None

        # clear the highlight
        self.clear_highlight()
        
    def enable_highlight(self):
        # highlight the search string
        self.update_highlight()

        # activate the callback to know when the buffer has changed
        self.src = gtkutil.signal_holder(self.buffer, "changed",
                                        self.on_txt_changed)
    
    
    def set_highlight(self, highlight):
        if highlight:
            self.enable_highlight()
        else:
            self.disable_highlight()

    def get_highlight(self):
        return self.src is not None
    

def has_search_entries(buff, search_text):
    """Returns if a certain buffer contains or not a search string"""
    entries = search_iterator(buff, search_text, start_in_cursor=False)
    for bounds in entries:
        return True
        
    return False


class _SearchMethod(core.BaseService, EventProvider):
    
    focus = core.Depends(interfaces.ICarretController)
    
    __gsignals__ = {
        "text-changed": _VOID_VOID
    }

    buffer = core.Depends("buffer")
    
    auto_cycle = True
    
    def get_auto_cycle(self):
        return self.auto_cycle
    
    def set_auto_cycle(self, cycle):
        self.auto_cycle = cycle

    orientation = interfaces.ORIENTATION_FORWARD
    def set_orientation(self, orientation):
        self.orientation = orientation
    
    def get_orientation(self):
        return self.orientation

    #############
    # search_text
    text = ""
    
    def get_text(self):
        return self.text
    
    def set_text(self, text):
        has_changed = self.text != text
        self.text = text
        
        if has_changed:
            # Text is changed, update the highlight
            self.emit("text-changed")
            
    ##################
    # Methods
    
    ###################
    # events callbacks
    def on_buffer_changed(self, *args):
        assert self.is_highlight_enabled
        self.update_highlight()
        
    def on_search_changed(self, search_text):
        # This might be called when we have the highlight disabled
        # in that case we need to ignore it
        if not self.is_highlight_enabled:
            return
        # The search has changed we need to update the highlight
        self.update_highlight()
    
    #############
    # the search
    def search(self, trigger=True):
        find_forward = self.get_orientation() is ORIENTATION_FORWARD
        
        search_text = self.text
        buff = self.buffer
        # If we have nothing to search we can just move on
        if search_text == "":
            return False
            
        bounds = search_iterator(buff, search_text, find_forward=find_forward)
        
        try:
            start_iter, end_iter = bounds.next()
            buff.place_cursor(start_iter)
            buff.select_range(start_iter, end_iter)
            self.focus.focus_carret()
            return True
        
        except StopIteration:
            # We have to cycle we need to:
            # 1. get the orientation of where we're searching
            # 2. find out if there are no entries at all
            # 3. move to the top/bottom and grab the next one
            
            if not has_search_entries(self.buffer, search_text):
                return False

            if find_forward:
                next_iter = self.buffer.get_start_iter()
            else:
                next_iter = self.buffer.get_end_iter()

            self.buffer.place_cursor(next_iter)
            
            self.search()
            
            return True




class _ReplaceMethod(core.BaseService, EventProvider):
    __gsignals__ = {
        "text-changed": _VOID_VOID,
    }
    
    search = core.Depends(interfaces.ISearch)
    buffer = core.Depends("buffer")
    
    ########################
    # Properties
    
    ##############
    # search_text
    def get_search_text(self):
        return self.search.get_text()

    text = ""
    
    def get_text(self):
        return self.text
    
    def set_text(self, text):
        has_changed = self.text != text
        
        self.text = text

        if has_changed:
            self.emit("text-changed")
    
    ## Methods
    
    def replace(self, select_after=True, bounds=None):
        """
        When bounds is not None then it is assumed that the user wants to replace
        the given bounds for the replaced text, thus they are not verified if they
        have 0 length(no bounds problem).
        """

        buff = self.buffer
        if bounds is None:
            bounds = buff.get_selection_bounds()
            if len(bounds) == 0:
                return False
                
            # Check if there's selected text and if it matches the search text
            selected_text = bounds[0].get_text(bounds[1])
            if selected_text != self.search.get_text():
                return False
        
        # If it does get the selection bounds
        start, end = bounds
        # Delete the old text
        buff.delete(start, end)
        # Insert the new text
        buff.insert(start, self.get_text())
        
        # Select the replaced text
        if select_after:
            start = buff.get_iter_at_mark(buff.get_insert())
            start.backward_chars(len(self.get_text()))
        
        return True

    def replace_all(self):
        # Copying the text and replacing it in pure python is way faster then
        # doing it using the TextView iterators
        buff = self.buffer
        # get initial bounds
        start_iter = buff.get_start_iter()
        end_iter = buff.get_end_iter()
        # get the text
        text = buff.get_text(start_iter, end_iter)
        # replace the occurrences
        text = text.replace(self.search.get_text(), self.get_text())
        # set the new text
        buff.set_text(text)

class _FileOperations(core.BaseService):

    __implements__ = interfaces.IFileOperations,
    is_new = True
    filename = None
    encoding = "utf-8"
    buffer = core.Depends("buffer")

    def get_filename(self):
        return self.filename
    
    def set_filename(self, filename):
        self.filename = filename
    
    def get_encoding(self):
        return self.encoding
    
    def set_encoding(self, encoding):
        self.encoding = encoding
    
    def get_is_new(self):
        return self.is_new
    
    def save(self):
        """Saves the current buffer to the file"""
        assert self.filename is not None
        buff = self.buffer
        data = buff.get_text(*buff.get_bounds())

        fd = SafeFileWrite(self.filename)
        try:
            fd.write(data)
        finally:
            fd.close()
        
        buff.set_modified(False)
        self.is_new = False

    def load(self):
        assert self.filename is not None
        
        buff = self.buffer

        fd = open(self.filename)
        try:
            data = fd.read()
        finally:
            fd.close()

        data = unicode(data, self.encoding)
        
        buff.begin_not_undoable_action()
        buff.set_text(data)
        buff.set_modified(False)
        buff.place_cursor(buff.get_start_iter())
        buff.end_not_undoable_action()
        self.is_new = False

    def get_modified(self):
        return self.buffer.get_modified()
        

class Buffer(core.BaseService):
    buffer = core.Depends("buffer")
    def get_text(self):
        return self.buffer.get_text(*self.buffer.get_bounds())
    
    def get_selected_text(self):
        return get_buffer_selection(self.buffer)
    
    def set_text(self, text):
        self.buffer.set_text(text)

    def select_all(self):
        self.buffer.select_range(*self.buffer.get_bounds())

def register_services(service_provider):
    service_provider.register_factory(_SearchMethod, interfaces.ISearch)
    service_provider.register_factory(_ReplaceMethod, interfaces.IReplace)
    service_provider.register_factory(_FileOperations, interfaces.IFileOperations)
    service_provider.register_factory(_HighlightSearch, interfaces.IHighlightSearch)
    service_provider.register_factory(Buffer, interfaces.IBuffer)

