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

import threading
import gobject

class AsyncTask(object):
    """
    AsyncTask is used to help you perform lengthy tasks without delaying
    the UI loop cycle, causing the app to look frozen. It is also assumed
    that each action that the async worker performs cancels the old one (if
    it's still working), thus there's no problem when the task takes too long.
    You can either extend this class or pass two callable objects through its
    constructor.
    
    The first on is the 'work_callback' this is where the lengthy
    operation must be performed. This object may return an object or a group
    of objects, these will be passed onto the second callback 'loop_callback'.
    You must be aware on how the argument passing is done. If you return an
    object that is not a tuple then it's passed directly to the loop callback.
    If you return `None` no arguments are supplied. If you return a tuple
    object then these will be the arguments sent to the loop callback.
    
    The loop callback is called inside Gtk+'s main loop and it's where you
    should stick code that affects the UI.
    """
    def __init__(self, work_callback=None, loop_callback=None):
        self.counter = 0
        
        if work_callback is not None:
            self.work_callback = work_callback
        if loop_callback is not None:
            self.loop_callback = loop_callback
    
    def start(self, *args, **kwargs):
        """
        Please note that start is not thread safe. It is assumed that this
        method is called inside gtk's main loop there for the lock is taken
        care there.
        """
        args = (self.counter,) + args
        threading.Thread(target=self._work_callback, args=args, kwargs=kwargs).start()
    
    def work_callback(self):
        pass
    
    def loop_callback(self):
        pass
    
    def _work_callback(self, counter, *args, **kwargs):
        ret = self.work_callback(*args, **kwargs)
        gobject.idle_add(self._loop_callback, (counter, ret))

    def _loop_callback(self, vargs):
        counter, ret = vargs
        if counter != self.counter:
            return
        
        if ret is None:
            ret = ()
        if not isinstance(ret, tuple):
            ret = (ret,)
            
        self.loop_callback(*ret)

class GeneratorTask(AsyncTask):
    """
    The diference between this task and AsyncTask is that the 'work_callback'
    returns a generator. For each value the generator yields the loop_callback
    is called inside Gtk+'s main loop.
    """
    def _work_callback(self, counter, *args, **kwargs):
        for ret in self.work_callback(*args, **kwargs):
            gobject.idle_add(self._loop_callback, (counter, ret))
