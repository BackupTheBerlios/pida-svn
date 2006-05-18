# -*- coding: utf-8 -*- 
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

# Copyright (c) 2006 Ali Afshar

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

# Main entry point into application so check sanity
import sanity
del sanity

import os
import sys

import gtk
import gobject, threading

import debugsession
from console import Console
from mainwindow import MainWindow
#from sourceviewer import SourceViewer
from toolbar import Toolbar, StatusBar
from threadviewer import ThreadsViewer
from breakpointviewer import BreakpointViewer
from namespaceviewer import AllNamespaceViewer, LocalsViewer, GlobalsViewer
from stackviewer import StackViewer, StackItem


class Application(object):

    def __init__(self, viewfactory, options):
        self.options = options
        self.main_window = viewfactory(self)
        self.session_manager = debugsession.SessionManager(self)
        self.console = Console(self)
        self.main_window.console = self.console
        self.stack = StackViewer(self)
        #self.namespace = AllNamespaceViewer(self)
        self.threads = ThreadsViewer(self)
        #self.source = SourceViewer(self)
        self.globals = GlobalsViewer(self)
        self.locals = LocalsViewer(self)
        self.status = StatusBar(self)
        self.breaks = BreakpointViewer(self)
        self.toolbar = Toolbar(self)
        debugsession.connect_events(self)

    def launch(self, filename):
        def _l(filename):
            import threading
            if filename is not None:
                def _t():
                    self.session_manager.launch(True, filename)
                t = threading.Thread(target=_t)
                t.start()
        _l(filename)
        #gobject.idle_add(_l, filename)

    def update_threads(self, event):
        current_thread = event.m_current_thread
        threads_list = event.m_thread_list
        def _u(threads_list, current_thread):
            self.threads.update_threads(threads_list, current_thread)
        gobject.idle_add(_u, threads_list, current_thread)

    def update_thread_broken(self, event):
        tid = event.m_tid
        def _u(tid):
            self.threads.broken_thread(tid)
        gobject.idle_add(_u, tid)

    def update_no_threads(self, event):
        print 'nothreads'

    def update_state(self, event):
        state = event.m_state
        def _u(state):
            self.status.update_running_status(state)
        def _u2(state):
            self.toolbar.update_state(state)
        def _u3(state):
            self.master.update_state(state)
        gobject.idle_add(_u, state)
        gobject.idle_add(_u2, state)
        gobject.idle_add(_u3, state)

    def update_frame(self, event):
        index = event.m_frame_index
        def _u(index):
            self.stack.select_frame(index)
        gobject.idle_add(_u, index)
        self.update_source(-index - 1)

    def update_stack(self, event):
        stack = event.m_stack
        self._last_stack = stack
        def _u(stack):
            self.stack.update_stack(stack)
        gobject.idle_add(_u, stack)
        self.update_source(-1)

    def update_source(self, index):
        def _u(index):
            si =StackItem(index, *self._last_stack['stack'][index])
            self.source_goto(si.filename, si.linenumber)
        gobject.idle_add(_u, index)
            
    def update_namespace(self, event):
        def _u():
            self.locals.update_namespace()
            self.globals.update_namespace()
        gobject.idle_add(_u)

    def update_bp(self, event):
        def _u(event):
            act = event.m_action
            if event.m_bp is not None:
                filename = event.m_bp.m_filename
                linenumber = event.m_bp.m_lineno
                index = event.m_bp.m_id
                indices = None
            else:
                filename = None
                linenumber = None
                index = None
                indices = event.m_id_list
            self.breaks.update_bp(act, index, indices, filename, linenumber)
            self.master.update_bp(act, index, indices, filename, linenumber)
        gobject.idle_add(_u, event)
        


def start(*args):
    options = debugsession.start(*args)
    app = Application(MainWindow, options)
    app.console.start()
    app.main_window.show_all()
    if sys.argv[1:]:
        fn = sys.argv[-1]
        if os.path.exists(fn):
            app.launch(fn)
    gtk.main()

def embed(parent, viewfactory, filename=None):
    def start_embedded(*args):
        options = debugsession.start(*args)
        app = Application(viewfactory, options)
        app.console.start()
        app.main_window.show_all()
        parent.app = app
        if filename:
            fn = filename
            if os.path.exists(fn):
                app.launch(fn)
    return debugsession.main(start_embedded)


def main():
    debugsession.main(start)


if __name__ == '__main__':
    gtk.threads_init()
    main()
