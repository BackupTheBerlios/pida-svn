

import unittest

from model import property_evading_setattr, get_defintion_attrs, get_groups
from model import ModelAttribute, Model
import attrtypes as types

class Blah:
    """A fake schema"""
    __order__ = ['meh', 'feh']
    class meh:
        """a mew mew fake schema"""
        __order__ = ['foo', 'blah']
        class foo:
            """foo"""
            label = 'foo'
            rtype = types.string
            default = 'yes'
        class blah:
            """blah"""
            label = 'blah'
            rtype = types.string
            default = 'no'
    class feh:
        """a feh feh group"""
        stock_id = 'banana'
        label = 'FEH'
        __order__ = ['ouch', 'gah']
        class ouch:
            """ouch"""
            label = 'ouch'
            rtype = types.string
            default = 'ouch'

        class gah:
            """gah"""
            label = 'gah'
            rtype = types.string
            default = 'gah'
            sensitive_attr = 'feh__ouch'
            dependents = ['feh__ouch']

    class _notme:
        pass

    @staticmethod
    def __markup__(self):
        return self.feh__gah

class BlahBlah(object):
    def __init__(self):
        self._g = None
        self.f = None
    def get_g(self):
        return self._g
    def set_g(self, val):
        self._g = val
    g = property(get_g, set_g)

BlahModel = Model.__model_from_definition__(Blah)

class test_model_setattr(unittest.TestCase):

    def setUp(self):
        self.b = BlahBlah()

    def test_a_plain(self):
        property_evading_setattr(self.b, 'f', 10)
        self.assertEqual(self.b.f, 10)

    def test_b_prop(self):
        property_evading_setattr(self.b, 'g', 10)
        self.assertEqual(self.b.g, 10)

class test_model_parse_schema(unittest.TestCase):

    def setUp(self):
        self.mdef = Blah

    def test_a_toplevel(self):
        tops = [c for c in get_defintion_attrs(self.mdef)]
        self.assertEqual(tops.pop(), self.mdef.feh)
        self.assertEqual(tops.pop(), self.mdef.meh)
        self.assertEqual(tops, [])

    def test_b_optlevel(self):
        top = [c for c in get_defintion_attrs(self.mdef)][0]
        opts = [c for c in get_defintion_attrs(top)]
        self.assertEqual(opts, [self.mdef.meh.foo, self.mdef.meh.blah])

class test_model_attr(unittest.TestCase):

    def setUp(self):
        attrs = [a for a in get_defintion_attrs(Blah.feh)]
        self.m1 = ModelAttribute.from_definition('feh', attrs[0])
        self.m2 = ModelAttribute.from_definition('feh', attrs[1])

    def test_name(self):
        self.assertEqual(self.m1.name, 'ouch')
        self.assertEqual(self.m2.name, 'gah')

    def test_label(self):
        self.assertEqual(self.m1.label, 'ouch')
        self.assertEqual(self.m2.label, 'gah')

    def test_doc(self):
        self.assertEqual(self.m1.doc, 'ouch')
        self.assertEqual(self.m2.doc, 'gah')

    def test_rtype(self):
        self.assertEqual(self.m1.rtype, types.string)
        self.assertEqual(self.m2.rtype, types.string)

    def test_default(self):
        self.assertEqual(self.m1.default, 'ouch')
        self.assertEqual(self.m2.default, 'gah')

    def test_key(self):
        self.assertEqual(self.m1.key, 'feh__ouch')
        self.assertEqual(self.m2.key, 'feh__gah')

    def test_sensitive_attr(self):
        self.assertEqual(self.m1.sensitive_attr, None)
        self.assertEqual(self.m2.sensitive_attr, 'feh__ouch')

    def test_dependents(self):
        self.assertEquals(self.m1.dependents, [])
        self.assertEquals(self.m2.dependents, ['feh__ouch'])

class test_parse_groups(unittest.TestCase):

    def setUp(self):
        self.groups = [g for g in get_groups(Blah)]
        self.n1, self.d1, self.l1, self.s1, self.a1  = self.groups[0]
        self.n2, self.d2, self.l2, self.s2, self.a2  = self.groups[1]

    def test_a_getgroups(self):
        self.assertEqual(len(self.groups), 2)

    def test_b_name(self):
        self.assertEqual(self.n1, 'meh')
        self.assertEqual(self.n2, 'feh')

    def test_c_doc(self):
        self.assertEqual(self.d1, 'a mew mew fake schema')
        self.assertEqual(self.d2, 'a feh feh group')

    def test_d_label(self):
        self.assertEqual(self.l1, 'meh')
        self.assertEqual(self.l2, 'FEH')

    def test_e_stock(self):
        self.assertEqual(self.s1, '')
        self.assertEqual(self.s2, 'banana')

    def test_f_attrs(self):
        self.assertEqual(len(self.a1), 2)
        self.assertEqual(len(self.a2), 2)

class test_model_class(unittest.TestCase):

    def setUp(self):
        self.a1 = BlahModel()

    def test_a_attrs(self):
        self.assert_(hasattr(BlahModel, '__model_attrs__'))
        self.assertEqual(self.a1.__model_attrs__,
                         BlahModel.__model_attrs__)

    def test_b_attrs_map(self):
        self.assert_(hasattr(BlahModel, '__model_attrs_map__'))
        self.assertEqual(self.a1.__model_attrs_map__,
                         BlahModel.__model_attrs_map__)
        self.assertEqual(set(self.a1.__model_attrs_map__.keys()),
            set(['meh__foo', 'meh__blah', 'feh__ouch', 'feh__gah']))

    def test_c_original_model(self):
        self.assert_(not hasattr(Model, '__model_attrs__'))
        self.assert_(not hasattr(Model, '__model_attrs_map__'))

    def test_d_dependents(self):
        self.assertEqual(len(self.a1.__model_dependents__['meh__foo']), 0)
        self.assertEqual(len(self.a1.__model_dependents__['feh__ouch']), 1)
        self.assertEqual(self.a1.__model_dependents__['feh__ouch'],
                         set(['feh__gah']))

    def test_e_groups(self):
        self.assert_(hasattr(self.a1, '__model_groups__'))
        self.assertEqual(self.a1.__model_groups__,
                         BlahModel.__model_groups__)
        self.assertEqual(len(self.a1.__model_groups__), 2)

    def test_f_observers(self):
        for attr in self.a1.__model_attrs_map__:
            self.assertEqual(self.a1.__model_observers__[attr], set())

    def test_g_blocked(self):
        for attr in self.a1.__model_attrs_map__:
            self.assertEqual(self.a1.__model_blocked__[attr], set())

    def test_h_markup(self):
        self.assertEqual('gah', self.a1.__model_markup__)

    def tearDown(self):
        pass

class test_model_setting(unittest.TestCase):

    def setUp(self):
        self.a1 = Blah()

if __name__ == '__main__':
    unittest.main()
