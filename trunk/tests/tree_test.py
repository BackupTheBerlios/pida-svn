
"""An example for GtkTestCase."""

import pida.utils.testing as testing
import pida.pidagtk.tree as tree

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
        
