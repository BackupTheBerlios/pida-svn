

import pida.core.command as command
from pida.core.testing import test, assert_equal

class MockCommand(object):

    def __init__(self):
        self.count = 0
        self.args = []
        self.kw = []

    def __call__(self, *args, **kw):
        self.count = self.count + 1
        self.args = args
        self.kw = kw
        return True
        
def c():
    mc = MockCommand()
    arg1 = command.argument('banana', True)
    arg2 = command.argument('melon', False)
    c1 = command.command('peel', mc, [])
    c2 = command.command('fruitbowl', mc, [arg1, arg2])
    return c1, c2, mc

@test
def call_good(self):
    c1, c2, mc = c()
    assert_equal(mc.count, 0)
    assert_equal(True, c1())
    assert_equal(mc.count, 1)

@test
def call_good_argument(self):
    c1, c2, mc = c()
    assert_equal(mc.count, 0)
    assert_equal(True, c2(banana='yellow'))
    assert_equal(mc.count, 1)
    assert_equal(mc.kw, {'banana': 'yellow'})

@test
def test_d_call_opt_argument(self):
    c1, c2, mc = c()
    assert_equal(mc.count, 0)
    assert_equal(True, c2(banana='yellow', melon='green'))
    assert_equal(mc.count, 1)
    assert_equal(mc.kw, {'banana': 'yellow', 
                         'melon': 'green'})
