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
import os
import time
import traceback

from cStringIO import StringIO

out = sys.stdout
err = sys.stderr
if not 'PIDA_DEBUG' in os.environ or not os.environ['PIDA_DEBUG']:
    sys.stderr = StringIO()
    sys.stdout = StringIO()

def w(text):
    out.write(text)
    out.flush()

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
    w('\b\b\b(%s)' % seconds)
    out.flush()
    if seconds == 0:
        out.write('\n')
        out.flush()
        callback(*args)
    else:
        gobject.timeout_add(1000, _ui_delay, seconds, callback, *args)

def block_delay(seconds):
    stime = time.time()
    ctime = stime
    while ctime - stime < seconds:
        ctime = time.time()
        gtk.main_iteration(False)

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
    e = sys.exc_info()
    return traceback.format_exc(e)

def _test(boss):
    failed = []
    errored = []
    w('Starting, total %s tests\n' % len(test.tests))
    for t in test.tests:
        tout = sys.stdout
        terr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        try:
            ret = t(boss)
            w('.')
        except AssertionError, e:
            w('F')
            outs = sys.stdout.getvalue()
            errs = sys.stderr.getvalue()
            failed.append((t, get_tb(), errs, outs))
        except Exception, e:
            w('E')
            outs = sys.stdout.getvalue()
            errs = sys.stderr.getvalue()
            errored.append((t, get_tb(), errs, outs))
        sys.stdout = tout
        sys.stderr = terr
    w('\nDone\n')
    for l, errname in [(failed, 'FAIL'), (errored, 'ERROR')]:
        for name, e, errs, outs in l:
            w('--\n')
            w('%s %s\n' % (errname, name))
            w(e)
            w('--\n')
            if len(outs):
                w('--\n')
                w('STDOUT\n')
                w('%s\n' % outs)
                w('--\n')
            if len(errs):
                w('--\n')
                w('STDERR\n')
                w('%s\n % errs')
                w('--\n')
            out.flush()
    boss.stop()
    #out.write(sys.stdout.read())
    #out.write(sys.stderr.read())
    #block_delay(2)
    #gtk.main_quit()
    sys.exit(0)

def self_test(boss):
    out.write('Self testing, ')
    if boss.get_service('editormanager').editor.NAME.startswith('vim'):
        delay = 5
    else:
        delay = 2
    out.write('delay %s seconds    ' % delay)
    out.flush()
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
from pida.tests.core import document, actions
from pida.tests.pidagtk import tree
from pida.tests.services import buffermanager


