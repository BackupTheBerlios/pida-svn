# -*- coding: utf-8 -*-
__license__ = "MIT License <http://www.opensource.org/licenses/mit-license.php>"
__copyright__ = "2005, Tiago Cogumbreiro"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"

import gtksourceview

from events import EventsDispatcher

from gtkutil import search_iterator, get_buffer_selection
from common import ChildObject

#####################
import tempfile
import os

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

class _SearchMethod(ChildObject):

    can_find_forward = False
    can_find_backwards = False
    
    __search_text = ""
    
    def __init__(self, parent):
        super(_SearchMethod, self).__init__(parent)
        self.search_tag = self.get_parent().create_tag(
            "search_markers",
            background="yellow",
            foreground="black",
        )
        self.events = self.create_events()
        
    #############
    # search_text
    def get_search_text(self):
        return self.__search_text
    
    def set_search_text(self, search_text):
        has_changed = self.__search_text != search_text
        self.__search_text = search_text
        
        if has_changed:
            # Text is changed, update the highlight
            if self.is_highlight_enabled:
                self.update_highlight()
            self._on_changed(search_text)
            
    search_text = property(get_search_text, set_search_text)
    
    
    def create_events(self):
        events = EventsDispatcher()
        self._no_more_entries = events.create_event("no-more-entries")
        self._on_changed = events.create_event("changed")
        #events.register("changed", self.on_search_changed)
        return events
    
    changed_source = None
    
    is_highlight_enabled = property(lambda self: self.changed_source is not None)
    
    ##################
    # Methods
    
    def clear_highlight(self):
        self.get_parent().remove_tag(
            self.search_tag,
            self.get_parent().get_start_iter(),
            self.get_parent().get_end_iter()
        )

    def update_highlight(self):
        # Remove old highlight
        self.clear_highlight()
        
        if self.search_text is None or self.search_text == "":
            # Nothing to highlight 
            return

        # Apply tag to found entries
        bounds = search_iterator(self.get_parent(), self.search_text, start_in_cursor=False)
        apply_tag = self.get_parent().apply_tag
        search_tag = self.search_tag
        
        # These are optimizations for:
        #for start, end in bounds:
        #     apply_tag(self.search_tag, start, end)

        # Use local pointers instead of dots
        # use the 'map' function
        apply_tag_cycle = lambda bounds: apply_tag(search_tag, bounds[0], bounds[1])
        map(apply_tag_cycle, bounds)

        

    def disable_highlight(self):
        assert self.is_highlight_enabled
        
        # No longer listen for the changed buffer
        self.get_parent().disconnect(self.changed_source)
        self.changed_source = None

        # clear the highlight
        self.clear_highlight()
        
    def enable_highlight(self):
        assert not self.is_highlight_enabled
        
        # highlight the search string
        self.update_highlight()
        # activate the callback to know when the buffer has changed
        self.changed_source = self.get_parent().connect("changed", self.on_buffer_changed)
    
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
    def __call__(self, find_forward=True):
        search_text = self.search_text
        # If we have nothing to search we can just move on
        if search_text is None or search_text == "":
            self.clear_highlight()
            return False
            
        bounds = search_iterator(self.get_parent(), search_text, find_forward=find_forward)
        
        try:
            start_iter, end_iter = bounds.next()
            self.get_parent().place_cursor(start_iter)
            self.get_parent().select_range(start_iter, end_iter)
            return True
        
        except StopIteration:
            self._no_more_entries(find_forward)
            return False




class _ReplaceMethod(ChildObject):
    def __init__(self, parent):
        super(_ReplaceMethod, self).__init__(parent)
        self._events = self.create_events()
    
    ########################
    # Properties
    
    ##############
    # search_text
    def get_search_text(self):
        return self.get_parent().search_text    

    search_text = property(get_search_text)
    
    ################
    # replace_text
    _replace_text = ""
    def get_replace_text(self):
        return self._replace_text
    
    def set_replace_text(self, replace_text):
        has_changed = self._replace_text != replace_text
        self._replace_text = replace_text
        if has_changed:
            self._on_changed(replace_text)
            
    replace_text = property(get_replace_text, set_replace_text)
    
    #################
    # events
    def create_events(self):
        events = EventsDispatcher()
        self._on_changed = events.create_event("changed")
        return events

    def get_events(self):
        return self._events
    
    events = property(get_events)
    
    #####################
    # Methods
    def __call__(self, select_after=True, bounds=None):
        """
        When bounds is not None then it is assumed that the user wants to replace
        the given bounds for the replaced text, thus they are not verified if they
        have 0 length(no bounds problem).
        """
        buff = self.get_parent()
        if bounds is None:
            bounds = buff.get_selection_bounds()
        
            # Check if there's selected text and if it matches the search text
            if get_buffer_selection(buff) != self.search_text:
                return False
        
        # If it does get the selection bounds
        start, end = bounds
        # Delete the old text
        buff.delete(start, end)
        # Insert the new text
        buff.insert(start, self._replace_text)
        
        # Select the replaced text
        if select_after:
            start = buff.get_iter_at_mark(buff.get_insert())
            start.backward_chars(len(self.replace_text))
        
        return True

        

class CulebraBuffer(gtksourceview.SourceBuffer):

    def __init__(self, filename = None, encoding = "utf-8"):
        gtksourceview.SourceBuffer.__init__(self)
        
        lm = gtksourceview.SourceLanguagesManager()
        self.languages_manager = lm
        language = lm.get_language_from_mime_type("text/x-python")
        self.set_highlight(True)
        self.set_language(language)
        
        self.filename = filename
        self.encoding = encoding

        self.search_component = _SearchMethod(self)
        self.replace_component = _ReplaceMethod(self)
        
    #########################
    # search_highlight
    def get_search_highlight(self):
        return self.search_component.is_highlight_enabled
    
    def set_search_highlight(self, highlight):
        assert self.search_highlight is not highlight
        if highlight:
            self.search_component.enable_highlight()
        else:
            self.search_component.disable_highlight()

    search_highlight = property(get_search_highlight, set_search_highlight)
    
    ##########################
    # search_text
    def get_search_text(self):
        return self.search_component.search_text
    
    def set_search_text(self, text):
        self.search_component.search_text = text
    
    search_text = property(get_search_text, set_search_text)
    
    ####################
    # replace_text
    def get_replace_text(self):
        return self.replace_component.replace_text
    
    def set_replace_text(self, text):
        self.replace_component.replace_text = text
    
    replace_text = property(get_replace_text, set_replace_text)

    #####################
    # filename
    def get_filename(self):
        if self.__filename is None:
            return "New File"
        return self.__filename
    
    def set_filename(self, filename):
        self.__filename = filename
    
    filename = property(get_filename, set_filename)
    
    ####################
    # encoding
    def get_encoding(self):
        return self.__encoding
    
    def set_encoding(self, encoding):
        self.__encoding = encoding
    
    encoding = property(get_encoding, set_encoding)
    
    ###################
    # is_new
    def get_is_new(self):
        return self.__filename is None
    
    is_new = property(get_is_new)
    
    #################
    # methods
    def replace_all(self):
        # Copying the text and replacing it in pure python is way faster then
        # doing it using the TextView iterators
        
        # get initial bounds
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        # get the text
        text = self.get_text(start_iter, end_iter)
        # replace the occurrences
        text = text.replace(self.search_text, self.replace_text)
        # set the new text
        self.set_text(text)
                    
    def search(self, *args, **kwargs):
        """
        search(find_forward=True)
        
        Returns True if it found the self.search_text.
        """
        return self.search_component(*args, **kwargs)
    
    def replace(self, *args, **kwargs):
        disable_highlight = self.search_highlight
        if disable_highlight:
            self.search_highlight = False
        replaced = self.replace_component(*args, **kwargs)
        if disable_highlight:
            self.search_highlight = True
        return replaced

    def save(self):
        """Saves the current buffer to the file"""
        assert self.filename is not None
        fd = SafeFileWrite(self.filename)
        fd.write(self.get_text(*self.get_bounds()))
        fd.close()
        self.set_modified(False)

