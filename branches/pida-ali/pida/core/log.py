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

import base
import logging

class Log(base.pidaobject):
    """ The PIDA logger """
    def init(self):
        frmt = logging.Formatter(
            '%(levelname)s %(message)s')
        hndlr = logging.StreamHandler()
        hndlr.setFormatter(frmt)
        self.__logger = logging.getLogger()
        self.__logger.addHandler(hndlr)
        self.__logger.setLevel(logging.DEBUG)

    def debug(self, source, msg):
        self.__logger.debug(self.__format(source, msg))

    def info(self, source, msg):
        self.__logger.info(self.__format(source, msg))

    def warn(self, source, msg):
        self.__logger.info(self.__format(source, msg))

    def error(self, source, msg):
        self.__logger.info(self.__format(source, msg))

    def __format(self, source, msg):
        """Do initial formatting on the message"""
        return '%s: %s' % (source, msg)

import unittest

class test_log(unittest.TestCase):

    def setUp(self):
        self.log = Log()

    def test_log(self):
        self.log.info('src', 'msg')


if __name__ == '__main__':
    unittest.main()

