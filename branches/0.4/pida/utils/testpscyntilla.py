import unittest
from pscyntilla import *

def write_to_file(filename, data):
    try:
        fd = open(filename, "w")
        fd.write(data)
    finally:
        fd.close()

def read_from_file(filename):
    try:
        fd = open(filename)
        data = fd.read()
    finally:
        fd.close()
    return data
    
class TestPscyntilla(unittest.TestCase):
    def test_load_save(self):
        editor = Pscyntilla()
        data = "foo"
        write_to_file("foo", data)
        
        editor.load_file("foo")
        assert not editor.get_is_modified()
        editor._sc.append_text("foo")
        assert editor.get_is_modified()
        editor.save()
        assert not editor.get_is_modified()
        new_data = read_from_file("foo")
           
        self.assertEquals(data + "foo", new_data)

if __name__ == '__main__':
    unittest.main()