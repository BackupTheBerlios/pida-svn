obtain = lambda foo: foo

class IEventProvider:
    def register_event(self, event_name, callback):
        """Registers to a certain event, this should return a
        subscription like object."""

ORIENTATION_FORWARD = True
ORIENTATION_BACKWARD = False

class ISearch(IEventProvider):
    events = "text-changed",
    
    ## Properties
    def get_text(self):
        """Returns the text that we're supposed to search"""
    def set_text(self, text):
        """Sets the text that we're supposed to search"""
        
    def set_orentation(self, orientation):
        """defines the type of orientation, one of ORIENTATION_FORWARD, ORIENTATION_BACKWARD"""
    def get_orientation(self):
        """Returns the type of orientation"""
    
    ## Optional properties
    def set_search_type(self, search_type):
        """Should define SIMPLE,RE_SEARCH and whatnot"""
    def get_search_type(self):
        """Returns the search type"""
    def get_auto_cycle(self):
        """Wether the search should cycle when reached the end"""
    def set_auto_cycle(self, auto_cycle):
        """Sets the auto_cycle property."""

    ## Methods
    def search(self):
        """Returns wether or the search was successful"""
    def has_search_forward(self):
        """Returns wether there are search results forward"""
    def has_search_backward(self):
        """Returns wether there are search result backward"""

    def count_last(self):
        """Should return the search entries after the user has ran 'search'
        method."""

class IHighlightSearch:
    def get_highlight(self):
        """The editor should highlight the found entries"""
    def set_highlight(self, highlight_search):
        """wether or not it's highlight the search entries"""

class IReplace(IEventProvider):
    search = obtain(ISearch)
    events = "text-changed",
    
    ## Properties
    def set_text(self, text):
        """The text to replace"""
    def get_text(self):
        """Returns the text to replace"""
    
    ## Methods
    def replace(self):
        """Replaces the next select entry or selects the next element.
        Returns a boolean to specify the success of the action."""
    def replace_all(self):
        """Returns the success of the action. No replacements meaning False."""



class IFileOperations(IEventProvider):
    events = ("filename-changed", "file-loaded", "file-saved", "modified")

    def get_modified(self):
        """Return if the file was modified"""

    def get_is_new(self):
        """Returns if a file is new"""

    def get_encoding(self):
        """Returns the filename encoding"""

    def set_encoding(self):
        """Sets the filename encoding"""

    def get_filename(self):
        """path to filename"""

    def set_filename(self):
        """set te filename"""

    def load(self):
        """Loads the filename contents to the buffer"""

    def save(self):
        """Saves the buffer contents to the filename"""

class ISelectColors:
    def set_font_color(self, color):
        """Changes the font color"""
    
    def set_background_color(self, color):
        """Changes the editor's background color"""

class ISelectFont:
    def set_font(self, font):
        """Changes the editor's font"""

class ISearchBar:
    def get_widget(self):
        """Returns the search bar widget"""

class IReplaceBar:
    def get_widget(self):
        """Returns the replace bar widget"""

class ICarretController:
    def focus_carret(self):
        """Moves focus to current carret location"""

    def goto_line(self, line):
        """Focus the carret to line `index`, base index starts at 0."""

class IActionGroupController:
    def set_action_group(self, action_group):
        """Defines the new action group associated with the provider"""

class IBuffer:
    def get_selected_text(self):
        """Returns the selected text"""
    
    def get_text(self):
        """Returns all the text in the buffer"""
    
    def set_text(self, text):
        """Sets all the test in the buffer"""

class IWidget:
    """This represents the actual editor widget"""