# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 The PIDA Project 

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import gobject

import sys

import traceback


class Tester(object):
    """
    Instances of this class are a decorator to denote a test function.
    """

    def __init__(self):
        self.tests = []
    
    def __call__(self, f):
        def _f(*args, **kw):
            return f(*args, **kw)
        _f.__name__ = f.__name__
        _f.__doc__ = f.__doc__
        self.tests.append(_f)
        return _f

test = Tester()

import pida.tests.core
from pida.tests.services import *

def _ui_delay(seconds, callback, *args):
    print seconds
    seconds = seconds - 1
    if seconds == 0:
        callback(*args)
    else:
        gobject.timeout_add(1000, _ui_delay, seconds, callback, *args)

def _shorten(*varls):
    rets = []
    for var in varls:
        sequ = ('%s' % var)
        if len(sequ) > 48:
            sequ = '%s...' % sequ[:48]
        rets.append(sequ)
    return tuple(rets)

def assert_in(item, sequence):
    try:
        assert item in sequence
    except AssertionError, e:
        e.args = ('%s is not in %s' % _shorten(item, sequence))
        raise e

def assert_equal(item1, item2):
    pass
        

def get_tb():
    return sys.exc_info()

def _test(boss):
    failed = []
    errored = []
    print 'Starting', len(test.tests)
    for t in test.tests:
        try:
            ret = t(boss)
            sys.stdout.write('.')
        except AssertionError, e:
            sys.stdout.write('F')
            failed.append((t, get_tb()))
        except Exception, e:
            sys.stdout.write('E')
            errored.append((t, get_tb()))
        sys.stdout.flush()
    print '\nDone'
    for name, e in failed + errored:
        print 'FAIL', name
        traceback.print_exc(e)

def self_test(boss):
    print 'Self testing'
    _ui_delay(1, _test, boss)

# The actual tests

@test
def check_important_services(boss):
    impt = ['buffermanager', 'editormanager', 'window', 'contexts',
            'projectmanager']
    services = dict([(s.NAME, s) for s in boss.services])
    for n in impt:
        assert_in(n, services)


