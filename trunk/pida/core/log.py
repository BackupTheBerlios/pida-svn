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

import os
import logging

class ViewLogging(logging.Handler):
    """
    Handler for logging to a view
    """
    def __init__(self,boss):
        logging.Handler.__init__(self)
        self.boss = boss
        print "ViewLogging started !!!" ## DEBUG

    def emit(self,record):
        """
        Emit a record.

        Format the record and send it
        """
        
        self.boss.call_command('logmanager', 'get', record=record)

        print "LOGGER : %s" % record
    
class pidalogger(object):
    """Logging mixin"""

    def __init__(self,*args,**kw):
        self.log = self.__build_logger(self.__class__.__name__)

    def __build_logger(self, name):
        format_str = ('%(levelname)s '
                      '%(module)s.%(name)s:%(lineno)s '
                      '%(message)s')
        format = logging.Formatter(format_str)
        handler = logging.StreamHandler()
        handler.setFormatter(format)
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        if 'PIDA_DEBUG' in os.environ:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logger.setLevel(level)
        return logger

    def set_view_handler(self):
        handler = ViewLogging(self)
        self.log.addHandler(handler)
