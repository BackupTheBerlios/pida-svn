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

import base

class ComponentGroup(base.pidaobject):

    def init(self, name):
        self.__name = name
        self.__components = {}

    def register(self, name, component):
        """Register a component."""
        self.__components[name] = component
        return component

    def get(self, name):
        """Return the named component, or None."""
        try:
            return self.__components[name]
        except KeyError:
            return None

    def get_name(self):
        """Return the name for the group."""
        return self.__name
    name = property(get_name)

    def __iter__(self):
        for k in self.__components:
            yield self.__components[k]

class ComponentManager(ComponentGroup):

    def add_group(self, name):
        return self.register(name, ComponentGroup(name))

import unittest

class test_components(unittest.TestCase):

    def test_group(self):
        g = ComponentGroup('foo')

    def test_groupname(self):
        g = ComponentGroup('foo')
        self.assertEqual(g.name, 'foo')

    def test_nonexistent(self):
        g = ComponentGroup('foo')
        self.assertEqual(g.get('foo'), None)

    def test_register(self):
        g = ComponentGroup('foo')
        g.register('banana', ['b'])
        self.assertEqual(g.get('banana'), ['b'])

    def test_manager(self):
        m = ComponentManager('root')

    def test_addgroup(self):
        m = ComponentManager('root')
        m.add_group('foo')
        self.assertEqual(m.get('foo').name, 'foo')


if __name__ == '__main__':
    unittest.main()

