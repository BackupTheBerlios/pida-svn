import unittest
from gens import *

class TestCamel(unittest.TestCase):
    def check(self, str1, str2):
        self.assertEquals(camel_to_gnu(str1), str2)
        
    def test_strings(self):
        self.check("", "")
        self.check("a", "a")
        self.check("a_a", "a_a")
        self.check("Foo1", "foo1")
        self.check("FooBar", "foo_bar")
        self.check("fooBar", "foo_bar")
        self.check("FooBRS", "foo_b_r_s")
        self.check("FaAaAa", "fa_aa_aa")
        self.check("aaaA", "aaa_a")
        self.check("aaaAa", "aaa_aa")
        self.check("aAAA", "a_a_a_a")
        self.check("fooUTF8", "foo_utf8")
        self.check("UTF8", "utf8")
        self.check("UTF8Bar", "utf8_bar")
 
if __name__ == '__main__':
    unittest.main()
