import components as binding
import unittest


class Comp1 (binding.Component):
    comp3 = binding.Obtain ("..")

class Comp2 (binding.Component):
    pass

class Comp3 (binding.Component):
    comp1 = binding.Make (Comp1)

class TestComponents (unittest.TestCase):
    def testObtain (self):
        c1 = Comp3()
        c2 = Comp3()
        self.failIf (c1 is c2)
        self.failIf (c1.comp1 is c2.comp1)
        self.failIf (c1.comp1.comp3 is c2.comp1.comp3)


if __name__ == '__main__':
    unittest.main ()