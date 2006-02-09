
"""An example for GtkTestCase."""

import pida.utils.testing as testing
import pida.pidagtk.tree as tree
import gtk
import gobject
class MockItem(object):

    def __init__(self, k, n):
        self.key = k
        self.n = n
        

class TreeTest1(testing.GtkTestCase):

    def test_1_mfs(self):
        self.t = tree.Tree()
        mfs = self.t.get_property('markup-format-string')
        self.assertEqual(mfs, '%(key)s')

    def test_2_set_mfs(self):
        self.t = tree.Tree()
        self.t.set_property('markup-format-string', 'banana')
        mfs = self.t.get_property('markup-format-string')
        self.assertEqual(mfs, 'banana')

    def test_3_add_item(self):
        self.t = tree.Tree()
        self.assertEqual(len(self.t.model), 0)
        i = MockItem('a', 'b')
        self.t.add_item(i)
        self.assertEqual(len(self.t.model), 1)
        for row in self.t.model:
            self.assertEqual(row[0], 'a')
            self.assertEqual(row[1].value, i)

    def test_4_add_item_with_key(self):
        self.t = tree.Tree()
        i = MockItem('a', 'b')
        self.t.add_item(i, key='z')
        self.assertEqual(len(self.t.model), 1)
        for row in self.t.model:
            self.assertEqual(row[0], 'z')
            self.assertEqual(row[1].value, i)

    def test_5_selected_key(self):
        self.t = tree.Tree()
        i = MockItem('k1', 'b')
        self.t.add_item(i)
        i = MockItem('k2', 'c')
        self.t.add_item(i)
        self.assertEqual(self.t.selected_key, None)
        self.t.set_selected('k1')
        self.assertEqual(self.t.selected_key, 'k1')
        self.t.set_selected('k2')
        self.assertEqual(self.t.selected_key, 'k2')

    def test_6_selected(self):
        self.t = tree.Tree()
        i = MockItem('k1', 'b')
        self.t.add_item(i)
        i2 = MockItem('k2', 'c')
        self.t.add_item(i2)
        self.assertEqual(self.t.selected, None)
        self.t.set_selected('k1')
        self.assertEqual(self.t.selected.value, i)
        self.assertNotEqual(self.t.selected.value, i2)
        self.t.set_selected('k2')
        self.assertEqual(self.t.selected.value, i2)
        self.assertNotEqual(self.t.selected.value, i)

    def test_7_clicked(self):
        self.t = tree.Tree()
        i = MockItem('k1', 'b')
        self.t.add_item(i)
        i2 = MockItem('k2', 'c')
        self.t.add_item(i2)
        self.assertEqual(self.t.selected, None)
        def _c(tv, item):
            # check it is None now
            self.assertEqual(tv.selected, None)
            def _i():
                # but is getting set in idle
                self.assertEqual(tv.selected, item)
            gtk.idle_add(_i)
        self.t.connect('clicked', _c)
        self.t.emit('clicked', self.t.model[0][1])

    def test_8_d_clicked(self):
        self.t = tree.Tree()
        i = MockItem('k1', 'b')
        self.t.add_item(i)
        i2 = MockItem('k2', 'c')
        self.t.add_item(i2)
        self.assertEqual(self.t.selected, None)
        def _c(tv, item):
            # check it is None now
            self.assertEqual(tv.selected, None)
            def _i():
                # but is getting set in idle
                self.assertEqual(tv.selected, item)
            gtk.idle_add(_i)
        self.t.connect('double-clicked', _c)
        self.t.emit('double-clicked', self.t.model[0][1])



        
