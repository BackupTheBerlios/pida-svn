# Nothing needs testing here
import unittest
from gtkutil import *


class Foo(object):
    calls = 0
    @getter_memoize
    def get_foo(self):
        self.calls += 1
        return "foo"
    
    foo = property(get_foo)


class Bar(Foo):
    def get_foo(self):
        return Foo.get_foo(self) + " bar"

    foo = property(get_foo)

class AFoo(object):
    calls = 0
    def get_foo(self):
        self.calls += 1
        return "foo"
    
    foo = property(get_foo)

class ABar(AFoo):
    def get_foo(self):
        return AFoo.get_foo(self) + " bar"

    foo = property(get_foo)

class TestMemoize(unittest.TestCase):
    def test_mem(self):
        f = Foo()
        self.assertEquals(0, f.calls) 
        self.assertEquals("foo", f.foo)
        self.assertEquals(1, f.calls) 
        f.foo
        self.assertEquals(1, f.calls) 
        f.foo
        self.assertEquals(1, f.calls) 
        f.foo
        self.assertEquals(1, f.calls) 
        b = Bar()
        self.assertEquals("foo bar", b.foo)

    def test_someth(self):
        f = AFoo()
        self.assertEquals("foo", f.foo)
        
        b = ABar()
        self.assertEquals("foo bar", b.foo)

if __name__ == '__main__':
    unittest.main()
