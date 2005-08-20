import unittest
import sys

main = unittest.main

import pida.main
pida = pida.main.Application()

class Test(unittest.TestCase):
    
    def __init__(self, *args):
        global pida
        self.pida = pida
        unittest.TestCase.__init__(self, *args)

