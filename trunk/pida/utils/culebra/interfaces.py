class ISearchReplaceComponent:
    events = ("replace-text-changed", "search-text-changed", "no-more-entries")

    # Methods
    def replace(self):
        """Returns a boolean of the success of the action"""
    def search(self):
        """Should find the next entry, return a boolean of the success"""
    def replace_all(self):
        """Returns a boolean of the success of the action"""
    def set_replace_text(self, text):
        """Sets the new text"""
    def get_replace_text(self):
        """returns the replace text"""

    # This might me optional
    def set_auto_cycle(self, auto_cycle):
        """Should define if trying to replace an entry cycles it or not when
        it reaches end/start of buffer."""

    # UI related stuff:
    def set_highlight_search(self, highlight_search):
        """Enable/disable highlighting on searched entries"""

class IFileOperations:
    events = ("filename-changed", "file-loaded", "file-saved")

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
