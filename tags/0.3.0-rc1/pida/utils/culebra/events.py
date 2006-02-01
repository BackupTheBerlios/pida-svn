# -*- coding: utf-8 -*-
# Copyright (C) 2005 Tiago Cogumbreiro <cogumbreiro@users.sf.net>
# $Id: components.py 570 2005-09-09 19:28:26Z cogumbreiro $

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

__all__ = "EventsDispatcher",

class EventSource:
    def __init__ (self, callbacks):
        self.callbacks = callbacks
    
    def __call__ (self, *args, **kwargs):
        for callback in self.callbacks:
            callback (*args, **kwargs)

class EventsDispatcher(object):
    """
    An event dispatcher is the central events object. To use it you must first
    create an event with the ``create_event`` method, this will return an
    event source which is basically the function you'll use to trigger the
    event. After that you register the callbacks. Its usage follows:
    
    >>> dispatcher = EventDispatcher()
    >>> evt_src = dispatcher.create_event ("on-ring-event")
    >>> 
    >>> def callback1 ():
    >>>     print "riiiing!"
    >>> 
    >>> dispatcher.register ("on-ring-event", callback1)
    >>> 
    >>> evt_src ()
    riiing
    >>> 
    """
    def __init__ (self):
        self._events = {}
        
    def create_event (self, event_name):
        self._events[event_name] = []
        return EventSource (self._events[event_name])
    
    def create_events (self, event_names, event_sources = None):
        """
        This is a utility method that creates or fills a dict-like object
        and returns it. The keys are the event names and the values are the
        event sources.
        """
        if event_sources is None:
            event_sources = {}
            
        for evt_name in event_names:
            event_sources[evt_name] = self.create_event (evt_name)
        return event_sources
    
    def event_exists (self, event_name):
        return event_name in self._events
    
    def register (self, event_name, callback):
        assert self.event_exists (event_name)
        self._events[event_name].append (callback)
    
    def unregister (self, event_name, callback):
        self._events[event_name].remove (callback)


