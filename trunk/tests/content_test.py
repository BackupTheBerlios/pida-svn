
import pida.utils.testing as testing
import pida.pidagtk.tree as tree
import gtk
import gobject

from pida.pidagtk.contentview import ContentBook, content_view

class ContentbookTest(testing.GtkTestCase):

    def setUp(self):
        testing.GtkTestCase.setUp(self)
        self.cb = ContentBook()

    def test1_empty(self):
        self.assertEqual(self.cb.get_n_pages(), 0)

    def test2_add(self):
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        self.assertEqual(self.cb.get_n_pages(), 1)
        self.assert_(self.cb.has_uid(cv.unique_id))

    def test2_remove(self):
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        self.assertEqual(self.cb.get_n_pages(), 1)
        self.assert_(self.cb.has_uid(cv.unique_id))
        self.cb.remove_view(cv)
        self.assertEqual(self.cb.get_n_pages(), 0)
        self.assert_(not self.cb.has_uid(cv.unique_id))

    def test3_newly_active(self):
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        self.assertEqual(self.cb.get_current_page(), 1)

    def test4_switch(self):
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        self.assertEqual(self.cb.get_current_page(), 1)
        self.cb.prev_page()
        self.assertEqual(self.cb.get_current_page(), 0)
        self.cb.next_page()
        self.assertEqual(self.cb.get_current_page(), 1)

    def test5_cycle(self):
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        self.assertEqual(self.cb.get_current_page(), 1)
        self.cb.next_page()
        self.assertEqual(self.cb.get_current_page(), 0)
        self.cb.prev_page()
        self.assertEqual(self.cb.get_current_page(), 1)

    def test6_empty(self):
        cv = content_view(service=None, prefix='view')
        self.cb.add(cv)
        def _e(cb):
            pass
        self.cb.connect('empty', _e)
        
        
