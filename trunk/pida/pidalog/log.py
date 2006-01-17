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

import logging

import pida.core.boss

import storelog

class keep_handler(logging.Handler):
    """
    Handler for storing the logs

    @param base where the logger will be able to find the store
    """
    def __init__(self,base):
        logging.Handler.__init__(self)
        self.base = base

    def emit(self,record):
        """
        Stores the record

        Here has to be executed push_record on the 
        """
        if hasattr(self.base,"logs"):
            self.base.logs.push_record(record.created,record)
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

class notification_handler(logging.Handler):
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

#def foo():
#    print "OH!"
#
#pida.log.critical("FOO %s %s",foo,"iface")       

#            print 'testing callback'
#            foo = record.args()
#            foo.call()
#        else:   
#            print 'has no attribute callback'

        try:
            self.base.call_command('logmanager', 'refresh', record=record)
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
    """
    PIDA Logging interface
    
    Every object in the program that wants to send log calls
    has to be child of this class (or related to one).

    By using a base class for all the objects of your application
    you'll enable logging for all these objects. Then you'll have
    to define init_log() to make it call the use_handler methods.

    If you need one of your object to log through different handlers
    than what you defined originally you can define init_log() in
    all of those children, and they'll be processed.

    The life cicle of this interface is :
    1/ inherit from pidalogger on your base object and give it a
       reference to your main object
    2/ define your own init_log() using one of the use_handler() methods 
    3/ create_log_storage() in the main object's thread in his __init__()
    Then the logger will work.
    To customize, redefine init_log() to manage your own handlers
    """

    # private interface
    def __build_logger(self, name):
        logger = logging.getLogger(name)
        
        logging.addLevelName(60,'USER_INPUT')
        
        level = logging.DEBUG
        logger.setLevel(level)
        return logger

    # public interface

    def create_log_storage(self):
        """
        Constructor of the storage
        
        This will create the logs reposity and will be used
        throughout the logging module

        It has to be called *before* __init__ in the main 
        application object's thread
        """
        self.logs = storelog.logs()

    def __init__(self,obj=None):
        """
        Constructor of the logger

        has to be called *after* create_log_storage(), or logs
        will only be enabled on standard output stream
        
        @param base is the base object where where you will have
               called create_log_storage()
        """
        format_str = ('%(levelname)s '
                      '%(module)s.%(name)s:%(lineno)s '
                      '%(message)s')
        self.__format = logging.Formatter(format_str)

        self.log = self.__build_logger(self.__class__.__name__)

        if hasattr(obj,'logs'):
            self.__base = obj
            self.use_keep_handler()
            self.init_log()
        else:
            self.use_stream_handler()

    def init_log(self):
        """
        This function tells the wanted logging behaviour.
        Calls of the following settings function will enable
        every behaviour
        """
        raise NotImplementedError
        
    def use_stream_handler(self,level=None):
        """
        This handler writes to STDOUT all informations
        """
        handler = logging.StreamHandler()
        if level != None:
            handler.setLevel(logging._levelNames[level])
        handler.setFormatter(self.__format)
        self.log.addHandler(handler)

    def use_keep_handler(self,level=None):
        handler = keep_handler(self.__base)
        if level != None:
            handler.setLevel(logging._levelNames[level])
        self.log.addHandler(handler)

    def use_notification_handler(self,level=None):
        if self.__base.logs == None:
            return False
        handler = notification_handler(self.__base)
        if level != None:
            handler.setLevel(logging._levelNames[level])
        handler.setFormatter(self.__format)
        self.log.addHandler(handler)
        return True

'''
def foo(bool):
    if bool == True:
        print "yeah !"
    else:
        print "ugh ?! :("

pida.log.log(60,"FOO %s %s %s","cb_yesno","Choose yes",foo)
'''
