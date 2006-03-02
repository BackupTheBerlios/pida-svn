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
import gtk
import sys
import time
import traceback

from StringIO import StringIO


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

def _ui_delay(seconds, callback, *args):
    seconds = seconds - 1
    sys.stdout.write('\b\b\b(%s)' % seconds)
    sys.stdout.flush()
    if seconds == 0:
        sys.stdout.write('\n')
        sys.stdout.flush()
        callback(*args)
    else:
        gobject.timeout_add(1000, _ui_delay, seconds, callback, *args)

def block_delay(seconds):
    stime = time.time()
    ctime = stime
    while ctime - stime < seconds:
        ctime = time.time()
        gtk.main_iteration(False)
        gtk.get_current_event()

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
    try:
        assert item1 == item2
    except AssertionError, e:
        e.args = '%s != %s' % _shorten(item1, item2)
        raise e

def assert_notequal(item1, item2):
    try:
        assert item1 != item2
    except AssertionError, e:
        e.args = '%s == %s' % _shorten(item1, item2)
        raise e

def get_tb():
    return sys.exc_info()

def _test(boss):
    failed = []
    errored = []
    print 'Starting, total', len(test.tests), 'tests'
    for t in test.tests:
        out = sys.stdout
        err = sys.stderr
        sys.stderr = StringIO()
        sys.stdout = StringIO()
        try:
            ret = t(boss)
            out.write('.')
        except AssertionError, e:
            out.write('F')
            failed.append((t, get_tb(), sys.stderr, sys.stdout))
        except Exception, e:
            out.write('E')
            errored.append((t, get_tb(), sys.stderr, sys.stdout))
        out.flush()
        sys.stdout = out
        sys.stderr = err
    print '\nDone'
    for l, errname in [(failed, 'FAIL'), (errored, 'ERROR')]:
        for name, e, out, err in l:
            print '--'
            print errname, name
            traceback.print_exc(e)
            print '--'
            out.seek(0)
            outs = out.read().strip()
            if len(outs):
                print '--'
                print 'STDOUT'
                print outs
                print '--'
            err.seek(0)
            errs = err.read().strip()
            if len(errs):
                print '--'
                print 'STDERR'
                print errs
                print '--'
    boss.stop()
    sys.exit(0)

def self_test(boss):
    sys.stdout.write('Self testing, ')
    if boss.get_service('editormanager').editor.NAME.startswith('vim'):
        delay = 5
    else:
        delay = 2
    sys.stdout.write('delay %s seconds    ' % delay)
    _ui_delay(delay, _test, boss)

# The actual tests

@test
def check_important_services(boss):
    impt = ['buffermanager', 'editormanager', 'window', 'contexts',
            'projectmanager']
    services = dict([(s.NAME, s) for s in boss.services])
    for n in impt:
        assert_in(n, services)

# Import the tests
from pida.tests.core import *
from pida.tests.services import buffermanager


