# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import nose

import pida.core.command as command
import pida.utils.testing as testing

setup = testing._setup

class test_a_argument(nose.TestCase):
    def setUp(self):
        self.a1 = command.argument('banana', False)
        self.a2 = command.argument('melon', True)

    def test_a_init(self):
        self.assert_(self.a1)
        self.assert_(self.a2)

    def test_b_name(self):
        self.assertEquals(self.a1.name, 'banana')
        self.assertEquals(self.a2.name, 'melon')

    def test_c_required(self):
        self.assertFalse(self.a1.required)
        self.assertTrue(self.a2.required)

class test_b_command(nose.TestCase):
    def setUp(self):
        self.__dummycount = 0
        self.__dummyargs = []
        self.__dummykw = {}
        arg1 = command.argument('banana', True)
        arg2 = command.argument('melon', False)
        self.c1 = command.command('peel', self.__dummy_callback, [])
        self.c2 = command.command('fruitbowl', self.__dummy_callback,
                                  [arg1, arg2])

    def __dummy_callback(self, *args, **kw):
        self.__dummycount = self.__dummycount + 1
        self.__dummyargs = args
        self.__dummykw = kw
        return True

    def test_a_init(self):
        self.assert_(self.c1)
        self.assert_(self.c2)

    def test_b_call_good(self):
        self.assertEquals(self.__dummycount, 0)
        self.assertTrue(self.c1())
        self.assertEquals(self.__dummycount, 1)

    def test_c_call_good_argument(self):
        self.assertEquals(self.__dummycount, 0)
        self.assertTrue(self.c2(banana='yellow'))
        self.assertEquals(self.__dummycount, 1)
        self.assertEquals(self.__dummykw, {'banana': 'yellow'})

    def test_d_call_opt_argument(self):
        self.assertEquals(self.__dummycount, 0)
        self.assertTrue(self.c2(banana='yellow', melon='green'))
        self.assertEquals(self.__dummycount, 1)
        self.assertEquals(self.__dummykw, {'banana': 'yellow',
                                           'melon': 'green'})

