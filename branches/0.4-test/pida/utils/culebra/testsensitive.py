import unittest
import sensitive
import gtk
import weakref

class TestSaveLinker(unittest.TestCase):
    def test_linker(self):
        buff = gtk.TextBuffer()
        act = gtk.Action("Fop", "", None, None)
        l = sensitive.SaveLinker(buff, act)
        ref = weakref.ref(l)
        l = None
        assert ref() is None
    

if __name__ == '__main__':
    unittest.main()
        