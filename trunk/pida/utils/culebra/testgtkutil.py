# Nothing needs testing here
import unittest
from gtkutil import *
import gtk

class TestSignalHolder(unittest.TestCase):
    entry = ""
    
    def on_changed(self, entry):
        self.text = entry.get_text()
        
    def test_simple_ref(self):
        
        entry = gtk.Entry()
        holder = SignalHolder(entry, "changed", self.on_changed)
        assert hasattr(holder, "destroy_source")
        entry.set_text("foo")
        self.assertEquals("foo", self.text)
        
        
        holder = None
        entry.set_text("bar")
        self.assertEquals("foo", self.text)

        holder = SignalHolder(entry, "changed", self.on_changed)
        entry.destroy()
        # holder.obj is a function that returns the object associated
        # with the holder
        assert holder.obj() is None
        entry.set_text("foo2")
        self.assertEquals("foo", self.text)
        
        

if __name__ == '__main__':
    unittest.main()
