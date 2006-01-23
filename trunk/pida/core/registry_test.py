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
import registry
import errors

import os
import tempfile


def setup():
    pass


class test_a_registry_item(unittest.TestCase):

    def setUp(self):
        self.r = registry.registry_item('foo', 'fooddoc', 'blah')

    def test_a_init(self):
        self.assert_(self.r)
        self.assertEquals(None, self.r.value)
        self.assertEquals(self.r.default, 'blah')

    def test_b_predefault(self):
        self.assertEqual(self.r.value, None)

    def test_c_setdefault(self):
        self.r.setdefault()
        self.assertEqual(self.r.value, 'blah')

    def test_d_doc(self):
        self.assertEquals(self.r.doc, 'fooddoc')

    def test_e_validate(self):
        self.assert_(self.r.validate('melon'))

    def test_f_serialize(self):
        self.r.setdefault()
        self.assertEquals(self.r.serialize(), 'blah')

    def test_g_unserialize(self):
        self.assertEquals(self.r.unserialize('baz'), 'baz')

    def test_h_set(self):
        self.r.value = 'banana'
        self.assertEquals(self.r.value, 'banana')

    def test_i_load(self):
        self.r.load('banana')
        self.assertEquals(self.r.value, 'banana')


class test_b_integer(unittest.TestCase):
    
    def setUp(self):
        self.r = registry.types.integer('foo', 1, 'foodoc')

    def test_a_unserialize_good(self):
        self.assertEquals(self.r.unserialize('1'), 1)

    def test_b_unserialize_bad(self):
        self.assertRaises(errors.BadRegistryDataError,
                          self.r.unserialize, 'foo')

    def test_c_load_good(self):
        self.r.load('1')
        self.assertEquals(self.r.value, 1)
        
    def test_d_load_bad(self):
        self.r.load('foo')
        self.assertEquals(self.r.value, None)


class test_c_boolean(unittest.TestCase):

    def setUp(self):
        self.r = registry.types.boolean('foo', True, 'foodoc')

    def test_a_unserialize_good(self):
        self.assertEquals(self.r.unserialize('1'), True)
        self.assertEquals(self.r.unserialize('True'), True)
        self.assertEquals(self.r.unserialize('true'), True)

    def test_b_unserialize_bad(self):
        self.assertEquals(self.r.unserialize('foo'), False)

    def test_c_load_good(self):
        self.r.load('1')
        self.assertEquals(self.r.value, True)
        
    def test_d_load_bad(self):
        self.r.load('foo')
        self.assertEquals(self.r.value, False)


class test_d_directory(unittest.TestCase):

    HOME = os.path.expanduser('~')

    def setUp(self):
        self.r = registry.types.directory('foo', 'foodoc', self.HOME)

    def test_a_valid(self):
        self.r.setdefault()
        self.assertEquals(self.r.value, self.HOME)

    def test_b_validate_good(self):
        self.assertEquals(self.r.validate(self.HOME), True)

    def test_c_validate_bad(self):
        self.assertEquals(self.r.validate('/___'), False)


class test_e_registry_group(unittest.TestCase):

    def setUp(self):
        self.r = registry.registry_group('foo', 'foodoc')

    def test_a_doc(self):
        self.assertEquals(self.r.doc, 'foodoc')

    def test_b_empty(self):
        self.__assert_length(0)

    def test_c_additem(self):
        ri = self.r.new('blah', 'blahdoc', 'baz', registry.registry_item)
        ri.setdefault()
        gri = self.r.get('blah')
        self.assertEquals(gri, ri)
        self.assertEquals(gri.value, 'baz')
        self.__assert_length(1)

    def test_d_deleteitem(self):
        ri = self.r.new('blah', 'blahdoc', 'baz', registry.registry_item)
        self.r.remove('blah')
        self.__assert_length(0)

    def test_e_badkey(self):
        self.assertEquals(self.r.get('banana'), None)

    def __assert_length(self, length):
        items = [i for i in self.r]
        self.assertEquals(len(items), length)

class test_f_registry(unittest.TestCase):

    def setUp(self):
        r = """
[foo]
blah = 1
baz = True
        """
        fd, self.filename = tempfile.mkstemp()
        os.write(fd, r)
        os.close(fd)
        self.r = registry.registry()
        group = self.r.add_group('foo', 'foodoc')
        group.new('blah', 'blahdoc', 2, registry.types.integer)
        group.new('baz', 'bazdoc', False, registry.types.boolean)
        self.r.load(self.filename)
        
    def test_a_get_grouup(self):
        group = self.r.get('foo')
        self.assert_(group)

    def test_b_getoption(self):
        self.assertEquals(self.r.get('foo').get('blah').value, 1)

    def tearDown(self):
        os.remove(self.filename)


def teardown():
    pass
    
