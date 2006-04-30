
from pida.core.testing import test, assert_equal, assert_notequal
import pida.pidagtk.tree as tree
import gtk
import gobject

from pida.pidagtk.contentview import ContentBook, content_view

@test
def empty(self):
    cb = ContentBook()
    assert_equal(cb.get_n_pages(), 0)

@test
def add(self):
    cb = ContentBook()
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    assert_equal(cb.get_n_pages(), 1)
    assert_equal(cb.has_uid(cv.unique_id), True)

@test
def remove(self):
    cv = content_view(service=None, prefix='view')
    cb = ContentBook()
    cb.add(cv)
    assert_equal(cb.get_n_pages(), 1)
    assert_equal(cb.has_uid(cv.unique_id), True)
    cb.remove_view(cv)
    assert_equal(cb.get_n_pages(), 0)
    assert_equal(cb.has_uid(cv.unique_id), False)

@test
def newly_active(self):
    cb = ContentBook()
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    assert_equal(cb.get_current_page(), 1)

@test
def switch(self):
    cb = ContentBook()
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    assert_equal(cb.get_current_page(), 1)
    cb.prev_page()
    assert_equal(cb.get_current_page(), 0)
    cb.next_page()
    assert_equal(cb.get_current_page(), 1)

@test
def cycle(self):
    cb = ContentBook()
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    assert_equal(cb.get_current_page(), 1)
    cb.next_page()
    assert_equal(cb.get_current_page(), 0)
    cb.prev_page()
    assert_equal(cb.get_current_page(), 1)

@test
def empty(self):
    cb = ContentBook()
    cv = content_view(service=None, prefix='view')
    cb.add(cv)
    def _e(cb):
        pass
    cb.connect('empty', _e)


def _cv():
    return content_view(service=None, prefix='svcprefix')

@test
def prefix(self):
    cv = _cv()
    assert_equal(cv.prefix, 'svcprefix')

@test
def service(self):
    cv = _cv()
    assert_equal(cv.service, None)

@test
def short_title(self):
    cv = _cv()
    assert_equal(cv.short_title, 'Untitled')

@test
def short_title_init(self):
    cv = content_view(service=None, prefix='svcprefix',
                           short_title='short')
    assert_equal(cv.short_title, 'short')

@test
def short_title_override(self):
    class C(content_view):
        SHORT_TITLE = 'short-over'
    cv = C(service=None, prefix='svcprefix')
    assert_equal(cv.short_title, 'short-over')
    cv = C(service=None, prefix='svcprefix',
                           short_title='short')
    assert_equal(cv.short_title, 'short')

@test
def long_title(self):
    cv = _cv()
    assert_equal(cv.long_title, 'Long title')

@test
def icon_name(self):
    cv = content_view(service=None, prefix='svcprefix',
                      icon_name='gtk-close')
    assert_equal(cv.icon_name, 'gtk-close')

@test
def icon(self):
    cv = content_view(service=None, prefix='svcprefix',
                      icon_name='gtk-close')
    i1 = cv.icon
    i2 = cv.icon
    assert_notequal(i1, i2)
    assert_equal(isinstance(i1, gtk.Image), True)
        

        
    
    
        
        
