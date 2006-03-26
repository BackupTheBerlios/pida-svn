import tempfile
import unittest
import buffers
from buffers import *
import interfaces
import core

class BufferCase(unittest.TestCase):
    def setUp(self):
        self.buffer = buffers.BaseBuffer()
        
        provider = core.ServiceProvider()
        register_services(provider)
        provider.register_service(self.buffer, "buffer")
        
        self.search = provider.get_service(interfaces.ISearch)
        self.replace = provider.get_service(interfaces.IReplace)
        self.highlight = provider.get_service(interfaces.IHighlightSearch)
        self.file_ops = provider.get_service(interfaces.IFileOperations)
    
    def do_search(self):
        return self.search.search()
    
    def do_replace(self):
        return self.replace.replace()
    
    def do_replace_all(self):
        return self.replace.replace_all()
    
    def searchEquals(self, text, search, count=1):
        self.buffer.set_text(text)
        
        self.search.set_text(search)
        
        self.buffer.place_cursor(self.buffer.get_start_iter())
        
        for val in range(count):
            assert self.search.search()
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
        self.search.set_text(search)
        self.replace.set_text(replace)
        self.replace.replace_all()
        self.textEquals(target)
    
    def replaceEquals(self, text, search, replace, target, offset=0, repeat=0):
        self.selectedTextEquals("")
        self.buffer.set_text(text)
        self.search.set_text(search)
        self.replace.set_text(replace)

        # Move to start
        self.buffer.place_cursor(self.buffer.get_start_iter())
        
        # selects next entry
        assert self.do_search()
        self.selectedTextEquals(search, "Search string %r not selected on %r" % (search, text))
        
        # Move the offset of search entries
        for val in range(offset):
            assert self.do_search()
        
        # replaces it
        assert self.do_replace()
        # Repeat if necessary
        for val in range(repeat):
            assert self.do_search()
            assert self.do_replace()
            
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
        assert self.do_search()
        assert self.do_replace()
        assert not self.do_search()
        assert not self.do_replace()

        
        self.replaceEquals(
            text = "abc 123 ghi 123",
            search = "123",
            replace = "jkl",
            target = "abc 123 ghi jkl",
            offset = 1
        )
        assert not self.do_search()
        assert not self.do_replace()
    
    def test_replace_multiple(self):
        self.replaceEquals(
            text = "abc 123 ghi 123",
            search = "123",
            replace = "def",
            target = "abc def ghi def",
            repeat = 1
        )
        assert not self.do_search()
        assert not self.do_replace()
        
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
        assert not self.do_search()
        
        # replaces it
        assert not self.do_replace()

        # Repeat if necessary
        for val in range(3):
            assert not self.do_search()
            assert not self.do_replace()
            
        self.textEquals(target, "Seach string not replace: %r != %r" % (text, target))

class TestSearch:#(BufferCase):
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
        hl = self.highlight
        assert not hl.get_highlight()
        hl.set_highlight(True)
        assert hl.get_highlight()
        
        hl.set_highlight(False)
        assert not hl.get_highlight()

    def test_highlight(self):
        
        self.highlight.set_highlight(True)
        
        self.searchEquals(
            text = "foo bar foo",
            search = "foo",
            count = 1
        )
        
        self.checkHighlight(True)
        assert self.search.search()
        self.checkHighlight(True)
        assert not self.search.search()
        self.checkHighlight(True)

    def test_no_highlight(self):
        self.searchEquals(
            text = "foo bar foo",
            search = "foo",
            count = 1
        )
        
        self.checkHighlight(False)
        assert self.search.search()
        self.checkHighlight(False)
        assert not self.search.search()
        self.checkHighlight(False)


    def test_half_highlight(self):
        self.searchEquals(
            text = "foo bar foo",
            search = "foo",
            count = 1
        )
        
        self.checkHighlight(False)
        assert self.search.search()
        self.highlight.set_highlight(True)
        self.checkHighlight(True)
        assert not self.search.search()
        self.checkHighlight(True)


def read_file(filename):
    fd = open(filename)
    try:
        data = fd.read()
    finally:
        fd.close()

    return data

def write_file(filename, data):
    fd = open(filename, "w")
    try:
        fd.write(data)
    finally:
        fd.close()

class TestFileOperations(BufferCase):
    def setUp(self):
        super(TestFileOperations, self).setUp()
        self.filenames = []
#        self.buff = BaseBuffer()
    
    def tearDown(self):
        for filename in self.filenames:
            try:
                os.unlink(filename)
            except OSError:
                pass

    def create_file(self):
        filename = tempfile.mktemp()
        self.filenames.append(filename)
        return filename

    def assertText(self, text):
        self.assertEquals(text, self.buffer.get_text(*self.buffer.get_bounds()))

    def assertNew(self):
        assert self.file_ops.get_is_new()

    def assertOld(self):
        assert not self.file_ops.get_is_new()

    def test_save_file(self):
        opers = self.file_ops
        self.assertNew()

        filename = self.create_file()
        opers.set_filename(filename)
        opers.set_encoding("utf-8")
        self.buffer.set_text("foo")
        self.assertNew()
        opers.save()
        self.assertOld()
        self.assertText(read_file(filename))

    def test_load_file(self):
        filename = self.create_file()
        write_file(filename, "foo")
        opers = self.file_ops
        opers.set_filename(filename)
        opers.load()
        self.assertText("foo")

if __name__ == '__main__':
    unittest.main()
