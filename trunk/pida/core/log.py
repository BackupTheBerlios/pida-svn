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
import pida.core.boss
import logging

class keep_handler(logging.Handler):
    """
    Handler for storing the logs
    """
    def __init__(self,base):
        logging.Handler.__init__(self)
        self.base = base

    def emit(self,record):
        """
        Stores the record
        """
        if hasattr(self.base,"boss"):
            self.base.boss.logs.push_record(record.created,record)
        else:
            logger = logging.getLogger(self.__class__.__name__)
            format_str = ('%(levelname)s '
                          '%(module)s.%(name)s:%(lineno)s '
                          '%(message)s')
            format = logging.Formatter(format_str)
            handler = logging.StreamHandler()
            handler.setFormatter(format)
            logger.addHandler(handler)
            logger.warn("Log record couldn't be saved :\n * %s"%format.format(record))

class view_handler(logging.Handler):
    """
    Handler for logging to a view
    """
    def __init__(self,base):
        logging.Handler.__init__(self)
        self.base = base

    def emit(self,record):
        """
        Emit a record.

        Format the record and send it
        """
        try:
            self.base.call_command('logmanager', 'refresh')
        except pida.core.boss.ServiceNotFoundError:
            logger = logging.getLogger(self.__class__.__name__)
            format_str = ('%(levelname)s '
                          '%(module)s.%(name)s:%(lineno)s '
                          '%(message)s')
            format = logging.Formatter(format_str)
            handler = keep_handler(self.base)
            handler.setFormatter(format)
            logger.addHandler(handler)
            logger.warn("service logmanager missing")

class pidalogger(object):
    """Logging mixin"""

    def __init__(self,*args,**kw):
        self.log = self.__build_logger(self.__class__.__name__)
        
    def __build_logger(self, name):
        logger = logging.getLogger(name)
        
        format_str = ('%(levelname)s '
                      '%(module)s.%(name)s:%(lineno)s '
                      '%(message)s')
        format = logging.Formatter(format_str)

        if False: ## TODO Use a preference for that
            handler = logging.StreamHandler()
            handler.setFormatter(format)
            logger.addHandler(handler)

        handler = keep_handler(self)
        handler.setFormatter(format)
        logger.addHandler(handler)

        level = logging.DEBUG
        logger.setLevel(level)
        return logger

    def set_view_handler(self):
        if 'PIDA_LOG' in os.environ:
            handler = view_handler(self)
            self.log.addHandler(handler)
            return True
        return False

