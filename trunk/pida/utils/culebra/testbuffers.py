import unittest
import buffers

class BufferCase(unittest.TestCase):
    def setUp(self):
        self.buffer = buffers.CulebraBuffer()
    
    def searchEquals(self, text, search, count=1):
        self.buffer.set_text(text)
        self.buffer.search_text = search
        self.buffer.place_cursor(self.buffer.get_start_iter())
        
        for val in range(count):
            assert self.buffer.search()
            self.textEquals(text)
    
    
    def selectedTextEquals(self, text, reason=None):
        selected_text = self.buffer.get_text(*self.buffer.get_selection_bounds())
        self.assertEquals(text, selected_text)
    
    def textEquals(self, text, reason=None):
        self.assertEquals(text, self.buffer.get_text(*self.buffer.get_bounds()), reason)
    
    def selectedTextEquals(self, text, reason=None):
        bounds = self.buffer.get_selection_bounds()
        if len(bounds) == 0:
            self.assertEquals(text, "", reason)
        else:
            self.assertEquals(text, self.buffer.get_text(*bounds), reason)
    
    def replaceAllEquals(self, text, search, replace, target):
        self.buffer.set_text(text)
        self.buffer.search_text = search
        self.buffer.replace_text = replace
        self.buffer.replace_all()
        self.textEquals(target)
    
    def replaceEquals(self, text, search, replace, target, offset=0, repeat=0):
        self.selectedTextEquals("")
        self.buffer.set_text(text)
        self.buffer.search_text = search
        self.buffer.replace_text = replace

        # Move to start
        self.buffer.place_cursor(self.buffer.get_start_iter())
        
        # selects next entry
        assert self.buffer.search()
        self.selectedTextEquals(search, "Search string %r not selected on %r" % (search, text))
        
        # Move the offset of search entries
        for val in range(offset):
            assert self.buffer.search()
        
        # replaces it
        assert self.buffer.replace()
        # Repeat if necessary
        for val in range(repeat):
            assert self.buffer.search()
            assert self.buffer.replace()
            
        self.textEquals(target, "Seach string not replace: %r != %r" % (text, target))

            

class TestReplace(BufferCase):
    def test_replace_all_multiple_occourrences(self):
        self.replaceAllEquals(
            text = "\nfoo\n bar\n\n",
            search = "\n",
            replace = "",
            target = "foo bar"
        )

    def test_replace_all_empty_text(self):
        self.replaceAllEquals(
            text = "",
            search = "",
            replace = "",
            target = ""
        )

        self.replaceAllEquals(
            text = "",
            search = "",
            replace = "foo",
            target = ""
        )

        self.replaceAllEquals(
            text = "",
            search = "foo",
            replace = "bar",
            target = ""
        )
        
    def test_replace_all_single_occurrence(self):
        self.replaceAllEquals(
            text = "foo bar",
            search = "foo",
            replace = "bar",
            target = "bar bar",
        )
        
    def test_replace_forward(self):
        self.replaceEquals(
            text = "abc \n ghi \n",
            search = "\n",
            replace = "def",
            target = "abc def ghi \n"
        )
        assert self.buffer.search()
        assert self.buffer.replace()
        assert not self.buffer.search()
        assert not self.buffer.replace()

        
        self.replaceEquals(
            text = "abc 123 ghi 123",
            search = "123",
            replace = "jkl",
            target = "abc 123 ghi jkl",
            offset = 1
        )
        assert not self.buffer.search()
        assert not self.buffer.replace()
    
    def test_replace_multiple(self):
        self.replaceEquals(
            text = "abc 123 ghi 123",
            search = "123",
            replace = "def",
            target = "abc def ghi def",
            repeat = 1
        )
        assert not self.buffer.search()
        assert not self.buffer.replace()
        
    def test_replace_nothing(self):
        text = "abc 123 ghi 123"
        search = "----"
        replace = "def"
        target = "abc 123 ghi 123"

        self.selectedTextEquals("")
        self.buffer.set_text(text)
        self.buffer.search_text = search
        self.buffer.replace_text = replace

        # Move to start
        self.buffer.place_cursor(self.buffer.get_start_iter())
        
        # selects next entry
        assert not self.buffer.search()
        
        # replaces it
        assert not self.buffer.replace()

        # Repeat if necessary
        for val in range(3):
            assert not self.buffer.search()
            assert not self.buffer.replace()
            
        self.textEquals(target, "Seach string not replace: %r != %r" % (text, target))

class TestSearch(BufferCase):
    def test_search(self):
        self.searchEquals(
            text = "foo1bar1foo",
            search = "1",
            count = 2,
        )
        assert not self.buffer.search()
        assert not self.buffer.search()
        # Search 1 backwards, because we are already selecting the last one
        assert self.buffer.search(False)
        # Now search 1 forward
        assert self.buffer.search()
        # And now it fails again
        assert not self.buffer.search()
        # And now it doesn't
        assert self.buffer.search(False)

    def test_search_nothing(self):
        self.searchEquals(
            text = "foo bar",
            search = "it doesn't exist",
            count = 0
        )
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search()
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)

    def test_search_empty_text(self):
        self.searchEquals(
            text = "",
            search = "it doesn't exist",
            count = 0
        )
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search()
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)

    def test_search_empty_search(self):
        self.searchEquals(
            text = "foo bar",
            search = "",
            count = 0
        )
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search()
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)


    def test_search_both_empty(self):
        self.searchEquals(
            text = "",
            search = "",
            count = 0
        )
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search()
        assert not self.buffer.search()
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)
        assert not self.buffer.search(False)


class TestHighlight(BufferCase):
    def checkHighlight(self, highlight):
        buff = self.buffer
        bounds = buff.get_selection_bounds()
        if len(bounds) == 0:
            return

        tag = self.buffer.get_tag_table().lookup("search_markers")
        assert tag is not None
        self.assertEquals(bounds[0].begins_tag(tag), highlight)
        self.assertEquals(bounds[1].ends_tag(tag), highlight)
    

    def test_defaults(self):
        assert not self.buffer.search_highlight
        self.buffer.search_highlight = True
        assert self.buffer.search_highlight
        self.buffer.search_highlight = False
        assert not self.buffer.search_highlight
        
    def test_highlight(self):
        self.buffer.search_highlight = True
        self.searchEquals(
            text = "foo bar foo",
            search = "foo",
            count = 1
        )
        
        self.checkHighlight(True)
        assert self.buffer.search()
        self.checkHighlight(True)
        assert not self.buffer.search()
        self.checkHighlight(True)

    def test_no_highlight(self):
        self.searchEquals(
            text = "foo bar foo",
            search = "foo",
            count = 1
        )
        
        self.checkHighlight(False)
        assert self.buffer.search()
        self.checkHighlight(False)
        assert not self.buffer.search()
        self.checkHighlight(False)

    def test_half_highlight(self):
        self.searchEquals(
            text = "foo bar foo",
            search = "foo",
            count = 1
        )
        
        self.checkHighlight(False)
        assert self.buffer.search()
        self.buffer.search_highlight = True
        self.checkHighlight(True)
        assert not self.buffer.search()
        self.checkHighlight(True)


if __name__ == '__main__':
    unittest.main()
