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
import os
import mimetypes
import stat
import gobject
class Buffer(object):
    
    def __init__(self, filename):
        self.__filename = filename
        self.__is_polling = False
        self.__reset()

    def __reset(self):
        self.__lines = []
        self.__string = ''
        self.__stat = self.__load_stat()
        self.__mimetype = None
        
    def __iter__(self):
        if self.__lines == []:
            for line in self.__load_lines():
                yield line
        else:
            for line in self.__lines:
                yield line

    def __len__(self):
        return self.__stat[stat.ST_SIZE]
    length = property(__len__)

    def __load_lines(self):
        try:
            f = open(self.__filename)
        except IOError:
            return
        for line in f:
            self.__lines.append(line)
        self.__string = ''.join(self.__lines)
        f.close()

    def __load_stat(self):
        try:
            stat_info = os.stat(self.__filename)
        except OSError:
            stat_info = [0] * 10
        return stat_info

    def __get_filename(self):
        return self.__filename
    filename = property(__get_filename)

    def __get_lines(self):
        if self.__lines == []:
            self.__load_lines()
        return self.__lines
    lines = property(__get_lines)
    
    def __get_string(self):
        if self.__string == '':
            self.__load_lines()
        return self.__string
    string = property(__get_string)
        
    def __get_stat(self):
        return self.__stat
    stat = property(__get_stat)

    def __get_mimetype(self):
        if self.__mimetype is None:
            mime_type, encoding = mimetypes.guess_type(self.__filename)
            if mime_type is None:
                self.__mimetype = ('', '')
            else:
                self.__mimetype = tuple(mime_type.split('/'))
        return self.__mimetype
    mimetype = property(__get_mimetype)

    def poll(self):
        new_stat = self.__load_stat()
        if new_stat != self.__stat:
            self.__stat = new_stat
            self.__reset()
            print "has changed"
        return self.__is_polling

    def start_polling(self):
        self.__is_polling = True
        gobject.timeout_add(3000, self.poll)

    def stop_polling(self):
        self.__is_polling = True


#b = Buffer('/home/ali/linkser.pyi')
#print b.mimetype
#print len(b), b.length
##print b.stat
#print b.string
