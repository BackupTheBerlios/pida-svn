
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

class ContentViewTest(testing.GtkTestCase):

    def setUp(self):
        testing.GtkTestCase.setUp(self)
        self.cv = content_view(service=None, prefix='svcprefix')

    def test1_prefix(self):
        self.assertEqual(self.cv.prefix, 'svcprefix')

    def test2_service(self):
        self.assertEqual(self.cv.service, None)

    def test3_short_title(self):
        self.assertEqual(self.cv.short_title, 'Untitled')

    def test4_short_title_init(self):
        self.cv = content_view(service=None, prefix='svcprefix',
                               short_title='short')
        self.assertEqual(self.cv.short_title, 'short')

    def test5_short_title_override(self):
        class C(content_view):
            SHORT_TITLE = 'short-over'
        self.cv = C(service=None, prefix='svcprefix')
        self.assertEqual(self.cv.short_title, 'short-over')
        self.cv = C(service=None, prefix='svcprefix',
                               short_title='short')
        self.assertEqual(self.cv.short_title, 'short')

    def test6_long_title(self):
        self.assertEqual(self.cv.long_title, 'Long title')

    def test7_icon_name(self):
        cv = content_view(service=None, prefix='svcprefix',
                          icon_name='gtk-close')
        self.assertEqual(cv.icon_name, 'gtk-close')

    def test8_icon(self):
        cv = content_view(service=None, prefix='svcprefix',
                          icon_name='gtk-close')
        i1 = cv.icon
        i2 = cv.icon
        self.assertNotEqual(i1, i2)
        self.assert_(isinstance(i1, gtk.Image))
        

        
    
    
        
        
