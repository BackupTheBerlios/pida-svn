# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

import nose

import pida.core.event as event
from pida.core.testing import test, assert_equal

class MockCallback(object):

    def __init__(self):
        self.count = 0
        self.args = []
        self.kw = {}

    def cb(self, *args, **kw):
        self.count = self.count + 1
        self.args = args
        self.kw = kw
        return True

def c():
    return event.event(), MockCallback()

def setUp(self):
    self.e = event.event()
    self.__dummycount = 0
    self.__dummyargs = []
    self.__dummykw = {}

@test
def create_event(self):
    e, cb = c()
    assert_equal(e.has_event('banana'), False)
    e.create_event('banana')
    assert_equal(e.has_event('banana'), True)

@test
def register_callback(self):
    e, cb = c()
    e.create_event('banana')
    e.register('banana', cb.cb)

@test
def emit_event(self):
    e, cb = c()
    e.create_event('banana')
    e.register('banana', cb.cb)
    assert_equal(cb.count, 0)
    e.emit('banana')
    assert_equal(cb.count, 1)
    assert_equal(cb.args, ())
    assert_equal(cb.kw, {})

@test
def emit_event_multiple(self):
    e, cb = c()
    e.create_event('banana')
    e.register('banana', cb.cb)
    assert_equal(cb.count, 0)
    e.emit('banana')
    assert_equal(cb.count, 1)
    e.emit('banana')
    assert_equal(cb.count, 2)
    e.emit('banana')
    assert_equal(cb.count, 3)
    
@test
def emit_event_with_argument(self):
    e, cb = c()
    e.create_event('banana')
    e.register('banana', cb.cb)
    assert_equal(cb.count, 0)
    e.emit('banana')
    assert_equal(cb.count, 1)
    e.emit('banana', parameter=1)
    assert_equal(cb.count, 2)
    assert_equal(cb.args, ())
    assert_equal(cb.kw, {'parameter': 1})
    
@test
def emit_event_bad_argument(self):
    e, cb = c()
    e.create_event('banana')
    e.register('banana', cb.cb)
    try:
        e.emit('banana', 1)
        raise AssertionError('TypeError not raised')
    except TypeError:
        pass

