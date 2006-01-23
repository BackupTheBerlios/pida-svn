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
import handlers

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
        
        level = logging.DEBUG
        logger.setLevel(level)
        return logger

    # public initialization interface

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

    def stop_logging(self):
        logger = logging.getLogger('')
        logger.removeHandler(self.__notify_handler)
        
    def use_stream_handler(self,level=None):
        """
        This handler writes to STDOUT all informations
        """
        handler = logging.StreamHandler()
        if level != None:
            handler.setLevel(logging._levelNames[level])
        handler.setFormatter(self.__format)
        self.log.addHandler(handler)

    def use_notification_handler(self,level=None,callback=None):
        """
        Enables callback on each log written
        """
        if self.__base.logs == None:
            return False
        logger = logging.getLogger('')
        self.__notify_handler = handlers.notification_handler(callback)
        if level != None:
            self.__notify_handler.setLevel(logging._levelNames[level])
        format_str = ('%(levelname)s '
                      '%(module)s.%(name)s:%(lineno)s ')
        self.__notify_handler.setFormatter(format_str)
        logger.addHandler(self.__notify_handler)
        return True

    def use_keep_handler(self,level=None):
        handler = handlers.keep_handler(self.__base)
        if level != None:
            handler.setLevel(logging._levelNames[level])
        self.log.addHandler(handler)
        self.__handler = handler

