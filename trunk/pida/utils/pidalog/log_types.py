# -*- coding: utf-8 -*- 

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
#Copyright (c) 2006 Bernard Pratz <bernard@pratz.net>

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
import types
import logging

class event_record(logging.LogRecord):
    def __init__(self,name,level,pathname,lineno,msg,args,
                    exc_info,callback,title,prefill,type):
        """
        Initialize a logging/event record with most interesting information,
        or question ;)
        """
        logging.LogRecord.__init__(self, name, level, pathname,
                                    lineno, msg, args, exc_info)
        self.__callback = callback
        self.title = title
        self.type = type
        self.answered_value = None
        self.prefill = prefill

    def callback(self,value):
        self.answered_value = value
        self.__callback(value)

class event_log(logging.Logger):
    def __make_record(self, name, level, fn, lno, msg, args, 
                                           exc_info, callback, title, prefill, type):
        """
        Overridden factory method that creates an event log record
        """
        return event_record(name, level, fn, lno, msg, args, 
                                exc_info, callback, title, prefill, type)

    def _log(self, level, msg, args, 
                exc_info=None,callback=None,title=None,prefill=None,type='log'):
        """
        Refactoring of the low-level logging which creates a LogRecord and
        then calls the handlers of this logger to handle the record to add
        event supports
        """
        if logging._srcfile:
            log_tuple = logging.Logger.findCaller(self)
            if len(log_tuple) == 3:
                fn, lno, func = log_tuple
            elif len(log_tuple) == 2:
                fn, lno = log_tuple
                func = '(unknown function)'
            
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if type(exc_info) != types.TupleType:
                exc_info = sys.exc_info()
        record = self.__make_record(self.name, level, fn, lno, msg, args, 
                                       exc_info, callback, title, prefill, type)
        self.handle(record)

    def input(self, msg, **kwargs):
        """
        Log an user input event that has to be used in order to get events
        with a greater priority, to get him to answer.
        """
        if self.manager.disable >= USER_INPUT:
            return
        if self.isEnabledFor(USER_INPUT):
            apply(self._log, (USER_INPUT, msg, []), kwargs)

    def notify(self, msg, **kwargs):
        """
        Log an user notification event that has to be used in order to 
        get events with a greater priority, in order to get him to react.
        """
        if self.manager.disable >=  USER_NOTIFY:
            return
        if self.isEnabledFor(USER_NOTIFY):
            apply(self._log, (USER_NOTIFY, msg, []), kwargs)

logging.setLoggerClass(event_log)

