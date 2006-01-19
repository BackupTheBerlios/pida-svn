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
import cPickle as pickle
import tempfile
import os

class data_record(object):
    pass    


class data_base(base.pidacomponent):


    def init(self, filename):
        self.__filename = filename
        self.__data = {}
        self.__read()

    def load(self):
        self.__read()

    def save(self):
        self.__write(self.__serialize())
        self.__read()

    def __read(self):
        self.__data = self.__unserialize()

    def __unserialize(self):
        try:
            f = open(self.__filename, 'r')
            data = pickle.load(f)
            f.close()
        except:
            data = {}
        return data

    def __serialize(self):
        data = pickle.dumps(self.__data)
        return data

    def __write(self, data):
        f = open(self.__filename, 'w')
        f.write(data)
        f.close()

    def sync(self):
        self.save()

    def close(self):
        pass

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __iter__(self):
        for key in self.__data:
            yield key

    def __contains__(self, key):
        return key in self.__data

    def __delitem__(self, key):
        del self.__data[key]


