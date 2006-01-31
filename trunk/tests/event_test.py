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

import unittest
import event

class test_a_event(unittest.TestCase):

    def setUp(self):
        self.e = event.event()
        self.__dummycount = 0
        self.__dummyargs = []
        self.__dummykw = {}

    def __dummy_callback(self, *args, **kw):
        self.__dummycount = self.__dummycount + 1
        self.__dummyargs = args
        self.__dummykw = kw
        return True

    def test_a_init(self):
        self.assert_(self.e)

    def test_b_create_event(self):
        self.assertFalse(self.e.has_event('banana'))
        self.e.create_event('banana')
        self.assertTrue(self.e.has_event('banana'))

    def test_c_register_callback(self):
        self.e.create_event('banana')
        self.e.register('banana', self.__dummy_callback)

    def test_d_emit_event(self):
        self.e.create_event('banana')
        self.e.register('banana', self.__dummy_callback)
        self.assertEquals(self.__dummycount, 0)
        self.e.emit('banana')
        self.assertEquals(self.__dummycount, 1)
        self.assertEquals(self.__dummyargs, ())
        self.assertEquals(self.__dummykw, {})

    def test_e_emit_event_multiple(self):
        self.e.create_event('banana')
        self.e.register('banana', self.__dummy_callback)
        self.assertEquals(self.__dummycount, 0)
        self.e.emit('banana')
        self.assertEquals(self.__dummycount, 1)
        self.e.emit('banana')
        self.assertEquals(self.__dummycount, 2)

    def test_f_emit_event_with_argument(self):
        self.e.create_event('banana')
        self.e.register('banana', self.__dummy_callback)
        self.assertEquals(self.__dummycount, 0)
        self.e.emit('banana', parameter=1)
        self.assertEquals(self.__dummycount, 1)
        self.assertEquals(self.__dummyargs, ())
        self.assertEquals(self.__dummykw, {'parameter': 1})

    def test_g_emit_event_bad_argument(self):
        self.e.create_event('banana')
        self.e.register('banana', self.__dummy_callback)
        self.assertRaises(TypeError, self.e.emit,
                         'banana', 1)
