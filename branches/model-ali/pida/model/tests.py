
"""One or two test cases for the model"""

import os
import unittest

import attrtypes as types
from persistency import load_model_from_ini, IniFileObserver
from model import property_evading_setattr, get_defintion_attrs, get_groups,\
                  ModelAttribute, Model, ModelGroup,\
                  BaseSingleModelObserver, BaseMultiModelObserver


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

            @staticmethod
            def fget(self):
                return 'no'

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

class MockSingleObserver(BaseSingleModelObserver):

    def __model_notify__(self, *args):
        if hasattr(self, 'notify'):
            self.notify(self, *args)

class MockMultiObserver(BaseMultiModelObserver):

    def __model_notify__(self, *args):
        if hasattr(self, 'notify'):
            self.notify(self, *args)

    def set_model(self, model):
        self._current = model

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
        self.a1 = BlahModel()

    def test_simple_attr(self):
        self.assertEqual(self.a1.feh__gah, 'gah')

    def test_fget_attr(self):
        self.assertEqual(self.a1.meh__blah, 'no')

    def test_set_simple_attr(self):
        self.a1.feh__gah = 'hag'
        self.assertEqual(self.a1.feh__gah, 'hag')

    def test_set_fget_attr(self):
        self.a1.meh__blah = 'yes'
        self.assertEqual(self.a1.meh__blah, 'no')

class test_observer(unittest.TestCase):

    def setUp(self):
        self._n = {}
        self.ma = ma = ['meh__blah', 'feh__gah']
        self.o1 = MockSingleObserver()
        self.o2 = MockSingleObserver(model_attributes=ma)
        self.o3 = MockMultiObserver()
        self.o4 = MockMultiObserver(model_attributes=ma,
                        current_callback=self.set_current)

    def set_current(self, item):
        self.current = item

    def notify(self, obs, model, attr, value):
        self._n[(obs, model, attr)] = value

    def test_a_all_attrs(self):
        self.assertEqual(self.o1.__model_attributes__, None)
        self.assertEqual(self.o3.__model_attributes__, None)

    def test_b_some_attrs(self):
        self.assertEqual(self.o2.__model_attributes__, self.ma)
        self.assertEqual(self.o4.__model_attributes__, self.ma)

    def test_c_current_callback(self):
        self.assertEqual(self.o4.current_callback, self.set_current)
        self.assertEqual(self.o3.current_callback(), None)

    def test_d_register_single_some_attrs(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        a1.__model_register__(self.o1, newma)
        for a in newma:
            self.assert_(self.o1 in a1.__model_observers__[a])
        for a in self.ma:
            self.assert_(self.o1 not in a1.__model_observers__[a])

    def test_e_model_attr(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        a1.__model_register__(self.o2, self.o2.__model_attributes__)
        for a in self.ma:
            self.assert_(self.o2 in a1.__model_observers__[a])
        for a in newma:
            self.assert_(self.o2 not in a1.__model_observers__[a])

    def test_f_no_attr(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        a1.__model_register__(self.o2)
        for a in self.ma:
            self.assert_(self.o2 in a1.__model_observers__[a])
        for a in newma:
            self.assert_(self.o2 in a1.__model_observers__[a])

    def test_g_register_from_observer_all(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        self.o1.set_model(a1)
        for a in newma:
            self.assert_(self.o1 in a1.__model_observers__[a])
        for a in self.ma:
            self.assert_(self.o1 in a1.__model_observers__[a])

    def test_h_register_from_observer_some(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        self.o2.set_model(a1)
        for a in newma:
            self.assert_(self.o2 not in a1.__model_observers__[a])
        for a in self.ma:
            self.assert_(self.o2 in a1.__model_observers__[a])

    def test_i_call_current_callback(self):
        a1 = BlahModel()
        self.o4.current_callback(a1)
        self.assertEqual(self.current, a1)

    def test_j_no_call_current(self):
        a1 = BlahModel()
        self.current = None
        self.o3.current_callback(a1)
        self.assertEqual(self.current, None)

    def test_h_initial_notify(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        self.o1.notify = self.notify
        self.o1.set_model(a1)
        for a in newma:
            self.assert_((self.o1, a1, a) in self._n)
        for a in self.ma:
            self.assert_((self.o1, a1, a) in self._n)
        self.assertEqual(self._n[(self.o1, a1, 'feh__ouch')], 'ouch')
        self.assertEqual(self._n[(self.o1, a1, 'feh__gah')], 'gah')
        self.assertEqual(self._n[(self.o1, a1, 'meh__blah')], 'no')
        self.assertEqual(self._n[(self.o1, a1, 'meh__foo')], 'yes')

    def test_i_initial_some_notify(self):
        a1 = BlahModel()
        newma = ['feh__ouch', 'meh__foo']
        self.o2.notify = self.notify
        self.o2.set_model(a1)
        for a in newma:
            self.assert_((self.o2, a1, a) not in self._n)
        for a in self.ma:
            self.assert_((self.o2, a1, a) in self._n)
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 'gah')
        self.assertEqual(self._n[(self.o2, a1, 'meh__blah')], 'no')

    def test_j_single_attribute(self):
        self.o2.notify = self.notify
        a1 = BlahModel()
        self.o2.set_model(a1)
        a1.feh__gah = 100
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 100)
        a1.feh__gah = 200
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 200)

    def test_k_block_attribute(self):
        self.o2.notify = self.notify
        a1 = BlahModel()
        self.o2.set_model(a1)
        a1.feh__gah = 100
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 100)
        a1.__model_block__(self.o2, ['feh__gah'])
        a1.feh__gah = 200
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 100)

    def test_l_unblock_attribute(self):
        self.o2.notify = self.notify
        a1 = BlahModel()
        self.o2.set_model(a1)
        a1.feh__gah = 100
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 100)
        a1.__model_block__(self.o2, ['feh__gah'])
        a1.__model_unblock__(self.o2, ['feh__gah'])
        a1.feh__gah = 200
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 200)

    def test_m_unregister_all_attrs(self):
        a1 = BlahModel()
        self.o2.set_model(a1)
        a1.__model_unregister__(self.o2, self.ma)
        for a in self.ma:
            self.assert_(self.o2 not in a1.__model_observers__[a])

    def test_n_unregister_one_attr(self):
        a1 = BlahModel()
        self.o2.set_model(a1)
        a1.__model_unregister__(self.o2, [self.ma[0]])
        self.assert_(self.o2 not in a1.__model_observers__[self.ma[0]])
        self.assert_(self.o2 in a1.__model_observers__[self.ma[1]])

    def test_o_update_model(self):
        a1 = BlahModel()
        self.o2.set_model(a1)
        self.o2.update_model('meh__foo', 100)
        self.assertEqual(a1.meh__foo, 100)

    def test_p_add_model(self):
        a1 = BlahModel()
        self.o3.add_model(a1)
        for a in self.ma:
            self.assert_(self.o3 in a1.__model_observers__[a])

    def test_q_two_observers(self):
        a1 = BlahModel()
        self.o1.notify = self.notify
        self.o2.notify = self.notify
        self.o1.set_model(a1)
        self.o2.set_model(a1)
        a1.feh__gah = 100
        self.assertEqual(self._n[(self.o1, a1, 'feh__gah')], 100)
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 100)

    def test_r_two_observers_some(self):
        a1 = BlahModel()
        self.o1.notify = self.notify
        self.o2.notify = self.notify
        self.o1.set_model(a1)
        self.o2.set_model(a1)
        a1.meh__foo = 100
        self.assertEqual(self._n[(self.o1, a1, 'meh__foo')], 100)
        self.assertRaises(KeyError,
            lambda *a: self._n[(self.o2, a1, 'meh__foo')], 100)

    def test_s_two_observers_update(self):
        a1 = BlahModel()
        self.o1.notify = self.notify
        self.o2.notify = self.notify
        self.o1.set_model(a1)
        self.o2.set_model(a1)
        self.o1.update_model('feh__gah', 100)
        self.assertEqual(self._n[(self.o1, a1, 'feh__gah')], 'gah')
        self.assertEqual(self._n[(self.o2, a1, 'feh__gah')], 100)

class test_model_group(unittest.TestCase):

    def setUp(self):
        self.mg = ModelGroup()
        self.om = self.mg.create_multi_observer(MockMultiObserver)
        self.os = self.mg.create_single_observer(MockSingleObserver)

    def test_a_add_model(self):
        a1 = BlahModel()
        self.mg.add_model(a1)
        for a in a1.__model_attrs_map__:
            self.assert_(self.om in a1.__model_observers__[a])

    def test_b_preadd_model(self):
        a1 = BlahModel()
        mg = ModelGroup()
        mg.add_model(a1)
        om = mg.create_multi_observer(MockMultiObserver)
        for a in a1.__model_attrs_map__:
            self.assert_(om in a1.__model_observers__[a])

    def test_c_set_current(self):
        a1 = BlahModel()
        om = self.mg.create_multi_observer(MockMultiObserver)
        self.mg.add_model(a1)
        self.mg.set_current(a1)
        self.assertEqual(a1, self.om._current)
        self.assertEqual(a1, om._current)

    def test_d_set_model(self):
        a1 = BlahModel()
        os = self.mg.create_single_observer(MockSingleObserver)
        self.mg.add_model(a1)
        self.mg.set_current(a1)
        self.assertEqual(a1, self.os._model)
        self.assertEqual(a1, os._model)

class test_ini(unittest.TestCase):

    def setUp(self):
        self.a1 = BlahModel()
        self.a2 = BlahModel()
        self.s1 = '/tmp/_banana1'
        self.s2 = '/tmp/_banana2'
        load_model_from_ini(self.s1, self.a1)
        load_model_from_ini(self.s2, self.a2)
        self.o = IniFileObserver()
        self.o.add_model(self.a1)
        self.o.add_model(self.a2)

    def test_a_save(self):
        self.a1.meh__foo = '100'
        a1 = BlahModel()
        load_model_from_ini(self.s1, a1)
        self.assertEqual(self.a1.meh__foo, a1.meh__foo)

    def test_b_no_save_fget(self):
        self.a1.meh__blah = '100'
        a1 = BlahModel()
        load_model_from_ini(self.s1, a1)
        self.assertEqual(self.a1.meh__blah, a1.meh__blah)
        self.assertNotEqual(100, a1.meh__blah)

    def tearDown(self):
        os.unlink(self.s1)
        os.unlink(self.s2)

if __name__ == '__main__':
    unittest.main()

