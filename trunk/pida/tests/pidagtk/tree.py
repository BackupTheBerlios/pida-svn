
"""An example for GtkTestCase."""

from pida.pidagtk.tree import Tree
from pida.pidagtk.contentview import content_view

import gtk
import gobject

from pida.core.testing import test, assert_equal, block_delay

class MockItem(object):

    def __init__(self, k, n):
        self.key = k
        self.n = n


def cv(boss):
    svc = boss.get_service('window')
    t = Tree()
    v = content_view(service=svc, prefix='test', widget=t)
    svc.call('append_page', bookname='view', view=v)
    v.show_all()
    return svc, v, t


def dv(boss, v):
    boss.call_command('window', 'remove_page', view=v)    

    
@test
def markup_format(boss):
    svc, v, t = cv(boss)
    mfs = t.get_property('markup-format-string')
    assert_equal(mfs, '%(key)s')
    t.set_property('markup-format-string', 'banana')
    mfs = t.get_property('markup-format-string')
    assert_equal(mfs, 'banana')
    dv(boss, v)

    
@test
def add_item(boss):
    svc, v, t = cv(boss)
    assert_equal(len(t.model), 0)
    i = MockItem('a', 'b')
    t.add_item(i)
    assert_equal(len(t.model), 1)
    for row in t.model:
        assert_equal(row[0], 'a')
        assert_equal(row[1].value, i)
    dv(boss, v)

    
@test
def add_many_items(boss):
    svc, v, t = cv(boss)
    for l in 'abcdefghijklmnopqrstuvwxyz':
        i = MockItem(l, l.upper())
        t.add_item(i)
    assert_equal(len(t.model), 26)
    dv(boss, v)


@test
def get(boss):
    svc, v, t = cv(boss)
    for l in 'abcdefghijklmnopqrstuvwxyz':
        i = MockItem(l, l.upper())
        t.add_item(i)
    for row in t.model:
        assert_equal('a', t.get(row.iter, 1).value.key)
        assert_equal('A', t.get(row.iter, 1).value.n)
        break
    dv(boss, v)


@test
def selected_path(boss):
    svc, v, t = cv(boss)
    for l in 'abcdefghijklmnopqrstuvwxyz':
        i = MockItem(l, l.upper())
        t.add_item(i)
    t.set_selected('a')
    assert_equal(t.selected.key, 'a')
    assert_equal(t.selected_key, 'a')
    t.set_selected('z')
    assert_equal(t.selected.key, 'z')
    assert_equal(t.selected_key, 'z')
    dv(boss, v)

@test
def clicked(boss):
    svc, v, t = cv(boss)
    for l in 'abcdefghijklmnopqrstuvwxyz':
        i = MockItem(l, l.upper())
        t.add_item(i)
    t.emit('clicked', t.model[2][1])
    dv(boss, v)
        
