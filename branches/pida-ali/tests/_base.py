# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2005 Ali Afshar aafshar@gmail.com

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
import sys
sys.path.insert(2, '/home/ali/working/pida2')

import unittest
import gtk
import sys

class TestcaseError(Exception):
    pass

class DebugView(gtk.TextView):

    def __init__(self, stdout):
        gtk.TextView.__init__(self)
        self.stdout = stdout

    def write(self, data):
        self.stdout.write(data)
        self.get_buffer().insert_at_cursor(data)

    def flush(self):
        self.stdout.flush()

class DebugWindow(gtk.Window):
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.vb = gtk.VBox()
        self.add(self.vb)
        self.e = DebugView(sys.stdout)
        self.vb.pack_start(self.e)
        sys.stdout = self.e

    def load(self, widget, widgargs=[]):
        self.widget = widget(*widgargs)
        self.vb.pack_start(self.widget)
        return self.widget

    def start(self):
        self.show_all()

class WidgetTestCase(object):
    WIDGET = gtk.Label
    WIDGET_ARGS = []
    
    def run_tests(self):
        self.start_up()
        for attr in dir(self):
            if attr.startswith("test_"):
                self.run_test(attr)
        self.tear_down()

    def run_test(self, name):
        print "Running test '%s'." % name
        func = getattr(self, name, None)
        try:
            func()
            while gtk.get_current_event() is not None:
                print "iteration"
                gtk.main_iteration()
            print "Success"
        except TestcaseError:
            print "Failed"
        except Exception, e:
            print "Error"
            print e

    def start_up(self):
        self.dw = DebugWindow()
        self.widget = self.dw.load(self.WIDGET, self.WIDGET_ARGS)
        self.dw.start()

    def tear_down(self):
        pass 

    def assert_(self, statement):
        print "Asserting"
        try:
            assert(statement)
        except AssertionError:
            raise TestcaseError

class LabelTest(WidgetTestCase):
    WIDGET = gtk.FileChooserWidget
    def test_label(self):
        print self.widget.list_shortcut_folders()
        for folder in self.widget.list_shortcut_folders():
            print folder
            self.widget.remove_shortcut_folder(folder)

if __name__ == '__main__':
    t = LabelTest()
    t.run_tests()
    gtk.main()
